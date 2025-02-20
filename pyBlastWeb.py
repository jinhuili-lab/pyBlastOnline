import requests
import time
import xml.etree.ElementTree as ET

# BLAST API 端点
BLAST_URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"

# 输入序列
query_sequence = "AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC"

# 1️⃣ 提交 BLAST 任务
params = {
    "CMD": "Put",
    "PROGRAM": "blastn",  # 核苷酸比对
    "DATABASE": "nt",     # NCBI nt 数据库
    "QUERY": query_sequence,
    "FORMAT_TYPE": "XML"  # 请求 XML 格式的输出，便于解析
}

response = requests.get(BLAST_URL, params=params)
if "RID" not in response.text:
    print("Fail, check it.")
    exit()

# 提取任务 ID
rid = response.text.split("RID = ")[1].split("\n")[0]
print(f"BLAST job ID: {rid}")

# 2️⃣ 轮询查询结果（等待 BLAST 完成）
while True:
    check_params = {"CMD": "Get", "RID": rid, "FORMAT_OBJECT": "SearchInfo"}
    check_response = requests.get(BLAST_URL, params=check_params)
    
    if "Status=READY" in check_response.text:
        print("BLAST finished")
        break
    else:
        print("BLAST calculating...")
        time.sleep(10)  # 每 10 秒检查一次

# 3️⃣ 获取 BLAST 结果（XML 格式）
result_params = {"CMD": "Get", "RID": rid, "FORMAT_TYPE": "XML"}
result_response = requests.get(BLAST_URL, params=result_params)

# 4️⃣ 解析 XML 只保留比对结果
root = ET.fromstring(result_response.text)

results = []
for hit in root.findall(".//Hit"):
    hit_id = hit.find("Hit_id").text  # NCBI 目标序列 ID
    hit_def = hit.find("Hit_def").text  # 目标序列描述
    hsp = hit.find(".//Hsp")  # 取第一个比对结果
    if hsp is not None:
        identity = hsp.find("Hsp_identity").text  # 相似度
        align_len = hsp.find("Hsp_align-len").text  # 比对长度
        evalue = hsp.find("Hsp_evalue").text  # E 值
        query_seq = hsp.find("Hsp_qseq").text  # 查询序列片段
        hit_seq = hsp.find("Hsp_hseq").text  # 目标序列片段
        
        results.append({
            "Hit ID": hit_id,
            "Description": hit_def,
            "Identity": f"{identity}/{align_len}",
            "E-value": evalue,
            "Query Seq": query_seq,
            "Hit Seq": hit_seq
        })

# 5️⃣ 输出整理后的比对结果
for r in results:
    print("\n" + "-" * 50)
    print(f"Hit ID: {r['Hit ID']}")
    print(f"Description: {r['Description']}")
    print(f"Identity: {r['Identity']}")
    print(f"E-value: {r['E-value']}")
    print(f"Query Seq: {r['Query Seq']}")
    print(f"Hit Seq: {r['Hit Seq']}")
