import argparse
import os.path

from components.gector.utils.helpers import read_lines
from components.gector.gector.gec_model import GecBERTModel


def predict_for_file(input_file, output_file, model, batch_size=32):
    test_data = read_lines(input_file)
    predictions = []
    cnt_corrections = 0
    batch = []
    for sent in test_data:
        batch.append(sent.split())
        if len(batch) == batch_size:
            preds, cnt = model.handle_batch(batch)
            predictions.extend(preds)
            cnt_corrections += cnt
            batch = []
    if batch:
        preds, cnt = model.handle_batch(batch)
        predictions.extend(preds)
        cnt_corrections += cnt

    with open(output_file, 'w') as f:
        f.write("\n".join([" ".join(x) for x in predictions]) + '\n')
    return cnt_corrections


def load_for_demo(use_roberta=True, gpu_id=0):
    model_path = os.path.join(os.path.dirname(__file__), 'models')
    if use_roberta:
        model_path = os.path.join(model_path, 'roberta_1_gector.th')
        transformer_model = 'roberta'
        special_tokens_fix = 1
        min_error_prob = 0.50
        confidence_bias = 0.20
    else:
        model_path = os.path.join(model_path, 'xlnet_0_gector.th')
        transformer_model = 'xlnet'
        special_tokens_fix = 0
        min_error_prob = 0.66
        confidence_bias = 0.35
    vocab_path = os.path.join(os.path.dirname(
        __file__), 'data', 'output_vocabulary', '')
    model = GecBERTModel(vocab_path=vocab_path,
                         model_paths=[model_path],
                         iterations=5,
                         model_name=transformer_model,
                         special_tokens_fix=special_tokens_fix,
                         min_error_probability=min_error_prob,
                         confidence=confidence_bias,
                         is_ensemble=0,
                         gpu_id=gpu_id)
    return model


# inference for demo
def predict_for_demo(lines, model, batch_size=32):
    test_data = [s.strip() for s in lines]
    predictions = []
    batch = []
    for sent in test_data:
        batch.append(sent.split())
        if len(batch) == batch_size:
            preds, cnt = model.handle_batch(batch)
            predictions.extend(preds)
            batch = []
    if batch:
        preds, cnt = model.handle_batch(batch)
        predictions.extend(preds)

    # output = '<eos>'.join([' '.join(x) for x in predictions])
    output = [' '.join(x) for x in predictions]
    return output


def main(args):
    # get all paths
    model = GecBERTModel(vocab_path=args.vocab_path,
                         model_paths=args.model_path,
                         max_len=args.max_len, min_len=args.min_len,
                         iterations=args.iteration_count,
                         min_error_probability=args.min_error_probability,
                         lowercase_tokens=args.lowercase_tokens,
                         model_name=args.transformer_model,
                         special_tokens_fix=args.special_tokens_fix,
                         log=False,
                         confidence=args.additional_confidence,
                         is_ensemble=args.is_ensemble,
                         weigths=args.weights)

    cnt_corrections = predict_for_file(args.input_file, args.output_file, model,
                                       batch_size=args.batch_size)
    # evaluate with m2 or ERRANT
    print(f"Produced overall corrections: {cnt_corrections}")


if __name__ == '__main__':
    # read parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path',
                        help='Path to the model file.', nargs='+',
                        required=True)
    parser.add_argument('--vocab_path',
                        help='Path to the model file.',
                        default='data/output_vocabulary'  # to use pretrained models
                        )
    parser.add_argument('--input_file',
                        help='Path to the evalset file',
                        required=True)
    parser.add_argument('--output_file',
                        help='Path to the output file',
                        required=True)
    parser.add_argument('--max_len',
                        type=int,
                        help='The max sentence length'
                             '(all longer will be truncated)',
                        default=50)
    parser.add_argument('--min_len',
                        type=int,
                        help='The minimum sentence length'
                             '(all longer will be returned w/o changes)',
                        default=3)
    parser.add_argument('--batch_size',
                        type=int,
                        help='The size of hidden unit cell.',
                        default=128)
    parser.add_argument('--lowercase_tokens',
                        type=int,
                        help='Whether to lowercase tokens.',
                        default=0)
    parser.add_argument('--transformer_model',
                        choices=['bert', 'gpt2', 'transformerxl',
                                 'xlnet', 'distilbert', 'roberta', 'albert'],
                        help='Name of the transformer model.',
                        default='roberta')
    parser.add_argument('--iteration_count',
                        type=int,
                        help='The number of iterations of the model.',
                        default=5)
    parser.add_argument('--additional_confidence',
                        type=float,
                        help='How many probability to add to $KEEP token.',
                        default=0)
    parser.add_argument('--min_error_probability',
                        type=float,
                        help='Minimum probability for each action to apply. '
                             'Also, minimum error probability, as described in the paper.',
                        default=0.0)
    parser.add_argument('--special_tokens_fix',
                        type=int,
                        help='Whether to fix problem with [CLS], [SEP] tokens tokenization. '
                             'For reproducing reported results it should be 0 for BERT/XLNet and 1 for RoBERTa.',
                        default=1)
    parser.add_argument('--is_ensemble',
                        type=int,
                        help='Whether to do ensembling.',
                        default=0)
    parser.add_argument('--weights',
                        help='Used to calculate weighted average', nargs='+',
                        default=None)
    args = parser.parse_args()
    main(args)
