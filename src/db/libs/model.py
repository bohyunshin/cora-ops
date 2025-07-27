import os
from typing import Dict

from gnn.inference.gcn import GCNInference


def generate_prediction(
    train_result_path: str = "./pretrained_weight/gcn",
) -> Dict[int, Dict]:
    # get latest train result for gcn
    files = [file for file in os.listdir(train_result_path) if file.endswith(".pt")]
    files.sort()
    latest_train_result = files[-1]

    # inference class for gcn
    gcn_inference = GCNInference(os.path.join(train_result_path, latest_train_result))
    probs, y_pred = gcn_inference.predict()

    # get hidden layer embeddings
    embeddings = gcn_inference.extract_embeddings("hidden")

    # get most similar id and scores using hidden layer embeddings
    top_k_id, top_k_score = gcn_inference.most_similar(embeddings)

    # make result as dict
    result_dict = gcn_inference.make_result_dict(
        probs, y_pred, embeddings, top_k_id, top_k_score
    )

    return result_dict
