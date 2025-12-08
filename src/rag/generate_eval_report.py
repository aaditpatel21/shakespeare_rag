import os
import pandas as pd
import matplotlib.pyplot as plt

def get_stats(df):
    total_questions = len(df)

    #Chunks score
    correct_chunk_found_df = df.loc[df['Correct id found'] == True]
    correct_chunk_found_num = len(correct_chunk_found_df)
    percent_score_chunks_found = correct_chunk_found_num/total_questions *100

    #AI eval score
    avg_ai_ans_score = df['AI Answer Evaluation'].sum()/total_questions
    percent_ai_eval_score = avg_ai_ans_score*100


    return percent_score_chunks_found,percent_ai_eval_score


def split_question_data(filename):
    df = pd.read_csv(filename)
    
    df_qtype1 = df.loc[df['Question Type'] =='Quote based question']
    df_qtype2 = df.loc[df['Question Type'] =='Conceptual question']
    df_qtype3 = df.loc[df['Question Type'] =='Play/act specific question']
    print(df.columns)

    total_chunk_score, total_ai_eval_score = get_stats(df)
    qtype1_chunk_score, qtype1_ai_eval_score = get_stats(df_qtype1)
    qtype2_chunk_score, qtype2_ai_eval_score = get_stats(df_qtype2)
    qtype3_chunk_score, qtype3_ai_eval_score = get_stats(df_qtype3)

    scores = {'total_chunk_score':total_chunk_score, 'total_ai_eval_score':total_ai_eval_score, 
              'qtype1_chunk_score':qtype1_chunk_score, 'qtype1_ai_eval_score':qtype1_ai_eval_score, 
              'qtype2_chunk_score':qtype2_chunk_score, 'qtype2_ai_eval_score':qtype2_ai_eval_score,
              'qtype3_chunk_score':qtype3_chunk_score, 'qtype3_ai_eval_score':qtype3_ai_eval_score}

    print(f'\n---Total Score for file: {filename}---\n')
    print(f'Questions asked: {len(df)}\nChunk Recall % score: {total_chunk_score}\nAI Eval Scoure: {total_ai_eval_score}\n')

    print(f'\n---Quote based question Scores---\n')
    print(f'Questions asked: {len(df_qtype1)}\nChunk Recall % score: {qtype1_chunk_score}\nAI Eval Scoure: {qtype1_ai_eval_score}\n')

    print(f'\n---Conceptual question Scores---\n')
    print(f'Questions asked: {len(df_qtype2)}\nChunk Recall % score: {qtype2_chunk_score}\nAI Eval Scoure: {qtype2_ai_eval_score}\n')

    print(f'\n---Play/act specific question Scores---\n')
    print(f'Questions asked: {len(df_qtype3)}\nChunk Recall % score: {qtype3_chunk_score}\nAI Eval Scoure: {qtype3_ai_eval_score}\n')

    return scores


if __name__ == '__main__':

    simple_rag_files = {'k5': r'eval_results\simple_rag_k_5_evaluation_120125.csv', 'k10':r'eval_results\simple_rag_k_10_evaluation_120125.csv','k25':r'eval_results\simple_rag_k_25_evaluation_120125.csv', 'k40':r'eval_results\simple_rag_k_40_evaluation_120125.csv'}
    
    reranker_simple_rag_files = {'k40_rk5': r'eval_results\reranker_rag_k_40_rk_5_evaluation_120225.csv', 'k40_rk10':r'eval_results\reranker_rag_k_40_rk_10_evaluation_120225.csv',
                                 'k200_rk5':r'eval_results\reranker_rag_k_200_rk_5_evaluation_120225.csv','k200_rk10':r'eval_results\reranker_rag_k_200_rk_10_evaluation_120225.csv'}
    

    #---Simple Rag Graph---
    scores= {}
    for key in simple_rag_files:
        scores[key] = split_question_data(simple_rag_files[key])
    

    x = [5,10,25,40]
    y_tot_chunk = [scores['k5']['total_chunk_score'],scores['k10']['total_chunk_score'],scores['k25']['total_chunk_score'],scores['k40']['total_chunk_score']]
    y_tot_ai_eval = [scores['k5']['total_ai_eval_score'],scores['k10']['total_ai_eval_score'],scores['k25']['total_ai_eval_score'],scores['k40']['total_ai_eval_score']]
    
    y_qtype1_chunk = [scores['k5']['qtype1_chunk_score'],scores['k10']['qtype1_chunk_score'],scores['k25']['qtype1_chunk_score'],scores['k40']['qtype1_chunk_score']]
    y_qtype1_ai_eval = [scores['k5']['qtype1_ai_eval_score'],scores['k10']['qtype1_ai_eval_score'],scores['k25']['qtype1_ai_eval_score'],scores['k40']['qtype1_ai_eval_score']]
    
    y_qtype2_chunk = [scores['k5']['qtype2_chunk_score'],scores['k10']['qtype2_chunk_score'],scores['k25']['qtype2_chunk_score'],scores['k40']['qtype2_chunk_score']]
    y_qtype2_ai_eval = [scores['k5']['qtype2_ai_eval_score'],scores['k10']['qtype2_ai_eval_score'],scores['k25']['qtype2_ai_eval_score'],scores['k40']['qtype2_ai_eval_score']]

    y_qtype3_chunk = [scores['k5']['qtype3_chunk_score'],scores['k10']['qtype3_chunk_score'],scores['k25']['qtype3_chunk_score'],scores['k40']['qtype3_chunk_score']]
    y_qtype3_ai_eval = [scores['k5']['qtype3_ai_eval_score'],scores['k10']['qtype3_ai_eval_score'],scores['k25']['qtype3_ai_eval_score'],scores['k40']['qtype3_ai_eval_score']]

    # --- Plots (Subplots Configuration) ---
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Sensitivity Analysis: RAG Performance vs. Context Size (k)', fontsize=16)

    # 1. Total Scores (Top Left)
    axs[0, 0].plot(x, y_tot_chunk, label='Retrieval Recall Total', marker='o', linestyle='-', linewidth=2, color='black')
    axs[0, 0].plot(x, y_tot_ai_eval, label='AI Evaluation Score Total', marker='o', linestyle='--', linewidth=2, color='black')
    axs[0, 0].set_title('Overall Performance (300 Questions)')
    axs[0, 0].set_ylabel('Score (%)')
    axs[0, 0].grid(True, linestyle='--', alpha=0.3)
    axs[0, 0].legend()

    # 2. Quote Based (Top Right)
    axs[0, 1].plot(x, y_qtype1_chunk, label='Retrieval Recall Quote', marker='x', linestyle='-', color='blue', alpha=0.5)
    axs[0, 1].plot(x, y_qtype1_ai_eval, label='AI Evaluation Quote', marker='x', linestyle='--', color='blue', alpha=0.5)
    axs[0, 1].set_title('Quote Based Questions (100 Questions)')
    axs[0, 1].grid(True, linestyle='--', alpha=0.3)
    axs[0, 1].legend()

    # 3. Conceptual (Bottom Left)
    axs[1, 0].plot(x, y_qtype2_chunk, label='Retrieval Recall Conceptual', marker='x', linestyle='-', color='green', alpha=0.5)
    axs[1, 0].plot(x, y_qtype2_ai_eval, label='AI Evaluation Conceptual', marker='x', linestyle='--', color='green', alpha=0.5)
    axs[1, 0].set_title('Conceptual Questions (100 Questions)')
    axs[1, 0].set_xlabel('k (Chunks Retrieved)')
    axs[1, 0].set_ylabel('Score (%)')
    axs[1, 0].grid(True, linestyle='--', alpha=0.3)
    axs[1, 0].legend()

    # 4. Play Specific (Bottom Right)
    axs[1, 1].plot(x, y_qtype3_chunk, label='Retrieval Recall Play/Act', marker='x', linestyle='-', color='red', alpha=0.5)
    axs[1, 1].plot(x, y_qtype3_ai_eval, label='AI Evaluation Play/Act', marker='x', linestyle='--', color='red', alpha=0.5)
    axs[1, 1].set_title('Play Specific Questions (100 Questions)')
    axs[1, 1].set_xlabel('k (Chunks Retrieved)')
    axs[1, 1].grid(True, linestyle='--', alpha=0.3)
    axs[1, 1].legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 


    # ---Reranker with embedding only graph---
    scores= {}
    for key in reranker_simple_rag_files:
        scores[key] = split_question_data(reranker_simple_rag_files[key])



    x= [5,10]
    y_tot_chunk_40 = [scores['k40_rk5']['total_chunk_score'],scores['k40_rk10']['total_chunk_score']]
    y_tot_ai_eval_40 = [scores['k40_rk5']['total_ai_eval_score'],scores['k40_rk10']['total_ai_eval_score']]
    y_tot_chunk_200 = [scores['k200_rk5']['total_chunk_score'],scores['k200_rk10']['total_chunk_score']]
    y_tot_ai_eval_200 = [scores['k200_rk5']['total_ai_eval_score'],scores['k200_rk10']['total_ai_eval_score']]

    y_q1_chunk_40 = [scores['k40_rk5']['qtype1_chunk_score'], scores['k40_rk10']['qtype1_chunk_score']]
    y_q1_ai_eval_40 = [scores['k40_rk5']['qtype1_ai_eval_score'], scores['k40_rk10']['qtype1_ai_eval_score']]
    y_q1_chunk_200 = [scores['k200_rk5']['qtype1_chunk_score'], scores['k200_rk10']['qtype1_chunk_score']]
    y_q1_ai_eval_200 = [scores['k200_rk5']['qtype1_ai_eval_score'], scores['k200_rk10']['qtype1_ai_eval_score']]

    y_q2_chunk_40 = [scores['k40_rk5']['qtype2_chunk_score'], scores['k40_rk10']['qtype2_chunk_score']]
    y_q2_ai_eval_40 = [scores['k40_rk5']['qtype2_ai_eval_score'], scores['k40_rk10']['qtype2_ai_eval_score']]
    y_q2_chunk_200 = [scores['k200_rk5']['qtype2_chunk_score'], scores['k200_rk10']['qtype2_chunk_score']]
    y_q2_ai_eval_200 = [scores['k200_rk5']['qtype2_ai_eval_score'], scores['k200_rk10']['qtype2_ai_eval_score']]
    
    y_q3_chunk_40 = [scores['k40_rk5']['qtype3_chunk_score'], scores['k40_rk10']['qtype3_chunk_score']]
    y_q3_ai_eval_40 = [scores['k40_rk5']['qtype3_ai_eval_score'], scores['k40_rk10']['qtype3_ai_eval_score']]
    y_q3_chunk_200 = [scores['k200_rk5']['qtype3_chunk_score'], scores['k200_rk10']['qtype3_chunk_score']]
    y_q3_ai_eval_200 = [scores['k200_rk5']['qtype3_ai_eval_score'], scores['k200_rk10']['qtype3_ai_eval_score']]

    # --- Plots (Subplots Configuration) ---
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Sensitivity Analysis: Reranker Performance vs. Context Size (k)', fontsize=16)

    # 1. Total Scores (Top Left)
    axs[0, 0].plot(x, y_tot_chunk_40, label='Retrieval Recall Total (initial k = 40)', marker='o', linestyle='-', linewidth=2, color='black')
    axs[0, 0].plot(x, y_tot_ai_eval_40, label='AI Evaluation Score Total (initial k = 40)', marker='o', linestyle='--', linewidth=2, color='black')
    axs[0, 0].plot(x, y_tot_chunk_200, label='Retrieval Recall Total (initial k = 200)', marker='o', linestyle='-', linewidth=2, color='blue')
    axs[0, 0].plot(x, y_tot_ai_eval_200, label='AI Evaluation Score Total (initial k = 200)', marker='o', linestyle='--', linewidth=2, color='blue')
    axs[0, 0].set_title('Overall Performance (300 Questions)')
    axs[0, 0].set_ylabel('Score (%)')
    axs[0, 0].grid(True, linestyle='--', alpha=0.3)
    axs[0, 0].legend()


    axs[0, 1].plot(x, y_q1_chunk_40, label='Recall (Init K=40)', marker='^', linestyle='-', color='black')
    axs[0, 1].plot(x, y_q1_ai_eval_40, label='Accuracy (Init K=40)', marker='^', linestyle='--', color='black')
    axs[0, 1].plot(x, y_q1_chunk_200, label='Recall (Init K=200)', marker='^', linestyle='-', color='blue')
    axs[0, 1].plot(x, y_q1_ai_eval_200, label='Accuracy (Init K=200)', marker='^', linestyle='--', color='blue')
    axs[0, 1].set_title('Quote Based Questions (Lexical)')
    axs[0, 1].grid(True, linestyle='--', alpha=0.3)
    axs[0, 1].legend()

    axs[1, 0].plot(x, y_q2_chunk_40, label='Recall (Init K=40)', marker='s', linestyle='-', color='black')
    axs[1, 0].plot(x, y_q2_ai_eval_40, label='Accuracy (Init K=40)', marker='s', linestyle='--', color='black')
    axs[1, 0].plot(x, y_q2_chunk_200, label='Recall (Init K=200)', marker='s', linestyle='-', color='blue')
    axs[1, 0].plot(x, y_q2_ai_eval_200, label='Accuracy (Init K=200)', marker='s', linestyle='--', color='blue')
    axs[1, 0].set_title('Conceptual Questions (Semantic)')
    axs[1, 0].set_ylabel('Score (%)')
    axs[1, 0].set_xlabel('Reranker Output (k2)')
    axs[1, 0].grid(True, linestyle='--', alpha=0.3)
    axs[1, 0].legend()

    axs[1, 1].plot(x, y_q3_chunk_40, label='Recall (Init K=40)', marker='d', linestyle='-', color='black')
    axs[1, 1].plot(x, y_q3_ai_eval_40, label='Accuracy (Init K=40)', marker='d', linestyle='--', color='black')
    axs[1, 1].plot(x, y_q3_chunk_200, label='Recall (Init K=200)', marker='d', linestyle='-', color='blue')
    axs[1, 1].plot(x, y_q3_ai_eval_200, label='Accuracy (Init K=200)', marker='d', linestyle='--', color='blue')
    axs[1, 1].set_title('Play Specific Questions (Metadata)')
    axs[1, 1].set_xlabel('Reranker Output (k2)')
    axs[1, 1].grid(True, linestyle='--', alpha=0.3)
    axs[1, 1].legend()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    #plt.show()


    filename = 'eval_results/reranker_hybrid_rag_k_40_10_rk_10_evaluation_120325.csv'

    scores = split_question_data(filename)

    filename = 'eval_results/reranker_hybrid_rag_k_25_25_rk_10_evaluation_120325.csv'

    scores = split_question_data(filename)

    filename = 'eval_results/reranker_hybrid_rag_k_10_40_rk_10_evaluation_120325.csv'

    scores = split_question_data(filename)

    filename = 'eval_results/reranker_hybrid_rag_k_160_40_rk_10_evaluation_120325.csv'

    scores = split_question_data(filename)

    filename = 'eval_results/reranker_hybrid_rag_k_200_80_rk_20_evaluation_120325.csv'

    scores = split_question_data(filename)
    filename = 'eval_results/reranker_hybrid_rag_k_320_80_rk_10_evaluation_120325.csv'

    scores = split_question_data(filename)
    filename = 'eval_results/reranker_hybrid_rag_k_80_20_rk_10_evaluation_120325.csv'

    scores = split_question_data(filename)

    filename = 'eval_results/reranker_hybrid_query_expansion_rag_k_80_15_rk_10_evaluation_120525.csv'

    scores = split_question_data(filename)

    filename = 'eval_results/reranker_hybrid_query_expansion_rag_k_160_30_rk_10_evaluation_120525.csv'

    scores = split_question_data(filename)

    filename = 'eval_results/reranker_hybrid_query_expansion_rag_fixed_prompt_k_80_15_rk_10_evaluation_120525.csv'

    scores = split_question_data(filename)