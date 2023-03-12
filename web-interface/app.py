import asyncio
from flask import Flask, render_template, request
import requests
import json
import os
import nltk
import spacy
import errant
import httpx
from errant.edit import Edit as ErrantEdit
import subprocess
from urllib.parse import quote
from sacremoses import MosesDetokenizer

import combinations.esc.run as esc
import combinations.memt.run as memt

import config

nlp = spacy.load("en_core_web_sm")
annotator = errant.load('en', nlp)
md = MosesDetokenizer(lang='en')

app = Flask(__name__)

selected_combination = config.selected_combination

file_path = os.path.dirname(os.path.realpath(__file__))
errant_path = os.path.join(file_path, 'errant_verbose.json')

with open(errant_path) as f:
    errant_verbose = json.load(f)

def postprocess(text):
    text = text.replace(' - ', '-')
    text = text.replace(" n't", "n't")
    # add more if needed
    return text


async def get_prediction(session, model, ori_texts, texts, edit_out):
    json_data = {'model' : model}
    model_config = config.models[model]
    json_data[model_config["request_key"]] = texts
    print('address', "{}:{}/{}".format(model_config["hostname"], model_config["port"], model_config['url']))
    response = await session.post(
                "{}:{}/{}".format(model_config["hostname"], model_config["port"], model_config['url']),
                json=json_data,
                timeout=None
               )
    if response.status_code == 200:
        outputs = response.json()[model_config["response_key"]]
    else:
        outputs = ''
        print(f'[ERROR] Failed to receive output from {model} API')
   
    print(model, 'api out:', outputs)
    assert len(texts) == len(outputs), "prediction length is different!"
    
    if edit_out:
        print('Parsing the edits...', flush=True)
        edits = []
        for s_idx, output in enumerate(outputs):
            e_out = annotator.parse(output)
            cur_edits = annotator.annotate(ori_texts[s_idx], e_out)
            e_data = {
                'source': texts[s_idx],
                'edits': []
            }
            for e in cur_edits:
                e_data['edits'].append((e.o_start, e.o_end, e.type, e.c_str))
            edits.append(e_data)
        return edits
    else:
        return outputs


@app.route('/', methods=['GET', 'POST'])
async def home():
    if request.method == 'POST':
        selected_combination = request.form.get('combination_select')
        models = request.form.getlist('models')
        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        analyze = request.form.get('analyze') is not None
        print('analyze: ', analyze)
        
        # separate input into lines and lines into sentences
        lines = request.form['input'].split('\n')
        sentences = []
        line_idx = []
        for l_idx, line in enumerate(lines):
            if len(line) == 0:
                continue
            l_sents = sent_detector.tokenize(line)
            for sent in l_sents:
                sentences.append(sent)
                line_idx.append(l_idx)

        print('Found {} sentence(s)'.format(len(sentences)))
        num_iter = (len(sentences) + config.BATCH_SIZE - 1) // config.BATCH_SIZE
        final_outs = []
        for i in range(num_iter):
            start = i * config.BATCH_SIZE
            end = min((i + 1) * config.BATCH_SIZE, len(sentences))
            texts = []
            e_ins = []
            for sentence in sentences[start:end]:
                # spacy_doc = nlp.pipe([sentence], disable=["tagger", "parser", "ner"])
                sentence = ' '.join(sentence.split()) # remove superflous spaces between words
                spacy_doc = annotator.parse(sentence, tokenise=True) # modified to comply with new spaCy syntax
                text = ' '.join([t.text for t in spacy_doc])
                texts.append(text)
                e_ins.append(spacy_doc)

            output_dict = {}
            edit_dict = {}
            async with httpx.AsyncClient() as session: # async client used for async function
                edit_out = (analyze and len(models) == 1) or (selected_combination == 'ESC' and len(models) > 1)
                tasks = [get_prediction(session, model, e_ins, texts, edit_out) for model in models]
                outputs = await asyncio.gather(*tasks, return_exceptions=True)
        
            if len(outputs) > 1:
                output_dict = {model: output for model, output in zip(models, outputs)}
                if selected_combination == 'ESC':
                    print('Running ESC', flush=True)
                    final_out = esc.predict(output_dict, generate_text=not analyze)
                elif selected_combination == 'MEMT':
                    print('Running MEMT', flush=True)
                    final_out = memt.predict(output_dict)
                    if analyze:
                        memt_edits = []
                        for s_idx, output in enumerate(final_out):
                            e_out = annotator.parse(output)
                            cur_edits = annotator.annotate(e_ins[s_idx], e_out)
                            e_data = {
                                'source': texts[s_idx],
                                'edits': []
                            }
                            for e in cur_edits:
                                e_data['edits'].append((e.o_start, e.o_end, e.type, e.c_str))
                            memt_edits.append(e_data)
                        final_out = memt_edits
                else:
                    raise NotImplementedError(f'Combination method {selected_combination} is not recognized.')

            elif len(outputs) == 1:
                final_out = outputs[0]
            else:
                alerts = {
                        'danger': 'Please select at least one component system'
                    }
                return render_template('home.html', input=request.form['input'], alerts=alerts,
                        combinations=config.combinations, models=models, analyze=analyze)
            final_outs.extend(final_out)

        out_lines = [[] for _ in lines]
        if len(sentences) == len(final_outs):
            for l_idx, out in zip(line_idx, final_outs):
                if analyze:
                    tokens = out['source']
                    if isinstance(tokens, str):
                        tokens = tokens.split(' ')
                    edits = out['edits']
                    offset = 0
                    for edit in edits:
                        if isinstance(edit, dict):
                            e_start = edit['start']
                            e_end = edit['end']
                            e_type = edit['type']
                            e_rep = edit['cor']
                        elif isinstance(edit, tuple):
                            e_start = edit[0]
                            e_end = edit[1]
                            e_type = edit[2]
                            e_rep = edit[3]
                        else:
                            raise ValueError("Data type {} is not supported."\
                                    .format(type(edit)))

                        e_rep = e_rep.strip()
                        op_type = e_type[0]
                        pos_type = e_type[2:]
                        errant_info = errant_verbose[pos_type]
                        title = errant_info["title"]
                        ori_str = ' '.join(tokens[e_start + offset:e_end + offset]).strip()
                        if pos_type == "ORTH":
                            # check if it's a casing issue
                            if ori_str.lower() == e_rep.lower():
                                if e_rep[0].isupper() and ori_str[0].islower():
                                    msg = "<b>{ori}</b> should be capitalized."
                                elif e_rep[0].islower() and ori_str[0].isupper():
                                    msg = "<b>{ori}</b> should not be capitalized."
                                else:
                                    msg = "The casing of the word <b>{ori}</b> is wrong."
                            # then it should be a spacing issue
                            else:
                                if len(ori_str) - 1 == len(e_rep):
                                    msg = "The word <b>{ori}</b> should not be written separately."
                                elif len(ori_str) + 1 == len(e_rep):
                                    msg = "The word <b>{ori}</b> should be separated into <b>{cor}</b>."
                                else:
                                    msg = "The word <b>{ori}</b> has orthography error."
                        else:
                            if op_type in errant_info:
                                msg = errant_info[op_type]
                            else:
                                msg = errant_verbose["Default"][op_type]
                        
                        msg = '<p>' + msg.format(ori=ori_str, cor=e_rep) + '</p>'

                        prefix = '<a tabindex="0" data-bs-html="true" role="button" ' + \
                                 'data-bs-toggle="popover" data-bs-trigger="focus" ' + \
                                 'data-bs-placement="top"  class="edit" ' + \
                                 f'title="{title}" data-bs-content="{msg}">'
                        suffix = '</a>'
                        e_cor = [prefix] + e_rep.split() + [suffix]
                        len_cor = len(e_cor)
                        tokens[e_start + offset:e_end + offset] = e_cor
                        offset = offset - (e_end - e_start) + len_cor
                    out = ' '.join(tokens)
                else:
                    sent = md.detokenize(out.split(' '))
                    out = postprocess(sent)
                out_lines[l_idx].append(out)
            str_out = '\n'.join([' '.join(l) for l in out_lines])
        else:
            print('[WARNING] the predicted sentence length ({}) is different from input ({})'\
                    .format(len(final_outs), len(sentences)))
            str_out = ' '.join(final_outs)
        str_out = '<p>' + str_out + '</p>'
        return render_template('home.html', input=request.form['input'], output=str_out, analyze=analyze,
                combinations=config.combinations, selected_combination=selected_combination, models=models)
    else:
        return render_template('home.html', combinations=config.combinations, selected_combination='ESC')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=4000, use_reloader=False)

