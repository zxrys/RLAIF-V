import random
from collections import defaultdict

from nltk import word_tokenize
from tqdm import tqdm

from data_engine.dpo_data_filter import filter
from data_engine.dpo_data_filter.similar_filter import SimilarFilter

data_pairs = []


def get_ranking_reward_data(rewards):
    sum_output = []
    avg_output = []

    # Group rewards by 'idx'
    grouped_data = defaultdict(list)
    for item in rewards:
        grouped_data[item['idx']].append(item)

    data_pairs = list(grouped_data.values())

    # Process each group
    for group in tqdm(data_pairs, desc="Processing groups"):
        # Sort the group by 'sum' and 'avg' in descending order
        sum_sorted_data = sorted(group, key=lambda x: x['sum'], reverse=True)
        avg_sorted_data = sorted(group, key=lambda x: x['avg'], reverse=True)

        # Assign ranks based on sorted order using enumerate for efficiency
        for rank, data in enumerate(sum_sorted_data, start=1):
            text = data['chosen']
            word_count = len(word_tokenize(text))
            sum_reward = data['sum']

            sum_data_dict = {
                "idx": data['idx'],
                "rank": rank,
                "word_count": word_count,
                "sum_reward": sum_reward,
                "question": data['question'],
                "image": data['image'],
                "text": text,
            }
            sum_output.append(sum_data_dict)

        for rank, data in enumerate(avg_sorted_data, start=1):
            text = data['chosen']
            word_count = len(word_tokenize(text))
            avg_reward = data['avg']

            avg_data_dict = {
                "idx": data['idx'],
                "rank": rank,
                "word_count": word_count,
                "avg_reward": avg_reward,
                "question": data['question'],
                "image": data['image'],
                "text": text,
            }
            avg_output.append(avg_data_dict)

    return sum_output, avg_output


def pair_union(sum_reward, avg_reward, sample_k=10, rank=3, strict_follow_rank=True, distance=25):
    print(f"sampling number k: {sample_k} \nrank number: {rank} \ndistance: {distance}")
    total_pairs = 0
    total_used_pic = 0
    flag = 0
    dpo_pair = []

    sum_reward_whole_data = list(sum_reward)
    avg_reward_whole_data = list(avg_reward)
    assert len(sum_reward_whole_data) == len(avg_reward_whole_data)

    # print(len(sum_reward_whole_data))

    for i in tqdm(range(0, len(sum_reward_whole_data), sample_k)):
        idx = sum_reward_whole_data[i]['idx']
        sum_reward_data = sum_reward_whole_data[i:i + sample_k]
        avg_reward_data = avg_reward_whole_data[i:i + sample_k]
        sum_reward_data = filter.filter_with_filter_list([SimilarFilter], sum_reward_data, log=False)
        avg_reward_data = filter.filter_with_filter_list([SimilarFilter], avg_reward_data, log=False)
        # top10 -> top rank
        sum_top_rank = sum_reward_data[:min(rank, len(sum_reward_data))]
        sum_last_rank = sum_reward_data[-min(rank, len(sum_reward_data)):]
        avg_top_rank = avg_reward_data[:min(rank, len(avg_reward_data))]
        avg_last_rank = avg_reward_data[-min(rank, len(avg_reward_data)):]

        avg_top_rank_text = [data['text'] for data in avg_top_rank]
        avg_last_rank_text = [data['text'] for data in avg_last_rank]

        # check the union
        chosen_answer = []
        rejected_answer = []
        question = ""
        for data in sum_top_rank:
            question = data["question"]
            if data['text'] in avg_top_rank_text:
                # print(f"chosen data: {data['text']}")
                # print(f"chosen word count: {data['word_count']}")
                chosen_answer.append((data['text'], data['word_count']))

        # print("*****")

        for data in sum_last_rank:
            if data['text'] in avg_last_rank_text:
                # print(f"rejected data: {data['text']}")
                # print(f"rejected word count: {data['word_count']}")
                rejected_answer.append((data['text'], data['word_count']))

        sign = 0
        # construct dpo pair if abs(dif(word_count)) < distance
        if strict_follow_rank:
            for chosen_data, rejected_data in zip(chosen_answer, rejected_answer):
                sign = 1
                dpo_pair.append({
                    "idx": idx,
                    "question": question,
                    "chosen": chosen_data[0],
                    "rejected": rejected_data[0],
                    "image": sum_reward_whole_data[i]['image']
                })
                total_pairs += 1
                if chosen_data[1] >= rejected_data[1]:
                    flag += 1
        else:
            random.shuffle(chosen_answer)
            random.shuffle(rejected_answer)
            for chosen_data in chosen_answer:
                for rejected_data in rejected_answer:
                    if abs(chosen_data[1] - rejected_data[1]) < distance:
                        sign = 1
                        dpo_pair.append({
                            "idx": idx,
                            "question": question,
                            "chosen": chosen_data[0],
                            "rejected": rejected_data[0],
                            "image": sum_reward_whole_data[i]['image']
                        })
                        total_pairs += 1
                        if chosen_data[1] >= rejected_data[1]:
                            flag += 1
        if sign == 1:
            total_used_pic += 1
    print(f"total_used_pic: {total_used_pic}")
    return dpo_pair


def main(rewards, sample_k=10, rank=3, strict_follow_rank=True, distance=25):
    sum_output, avg_output = get_ranking_reward_data(rewards)
    dpo_pair = pair_union(sum_output, avg_output, sample_k, rank, strict_follow_rank, distance)
    return dpo_pair, sum_output, avg_output


if __name__ == "__main__":
    pass
    # args = argparse.ArgumentParser()
    # args.add_argument("--reward_file", type=str, default="", help="The file path of the reward data.")
    # args.add_argument("--dpo_pair_file", type=str, default="", help="The output file path of the dpo pair data.")
    # args.add_argument("--sample_k", type=int, default=10, help="The sample number k.")
    # args.add_argument("--rank", type=int, default=10, help="The rank number.")
    # args.add_argument("--distance", type=int, default=5, help="The distance.")
    # args = args.parse_args()
    #
    # dpo_pair = main(args.reward_file, args.sample_k, args.rank, args.distance)
    # with jsonlines.open(args.output_file, 'w') as writer:
    #     writer.write_all(dpo_pair)
