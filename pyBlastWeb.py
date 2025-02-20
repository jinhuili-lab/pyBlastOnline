import gradio as gr
import requests
import time
import pandas as pd

# NCBI BLAST API endpoint
BLAST_URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"

# BLAST output format options
BLAST_FORMATS = {
    "Plain Text": "TEXT"
}

def run_blast(query_sequence, output_format):
    format_type = BLAST_FORMATS[output_format]
    format_params = {"FORMAT_TYPE": format_type}

    # 1️⃣ Submit the BLAST job
    params = {
        "CMD": "Put",
        "PROGRAM": "blastn",
        "DATABASE": "nt",
        "QUERY": query_sequence,
        **format_params  # Add the selected format parameters
    }

    response = requests.get(BLAST_URL, params=params)
    if "RID" not in response.text:
        return "❌ Submission failed! Please check the sequence format.", None

    rid = response.text.split("RID = ")[1].split("\n")[0]
    print(f"BLAST Job ID: {rid}")

    # 2️⃣ Poll the job status
    while True:
        check_params = {"CMD": "Get", "RID": rid, "FORMAT_OBJECT": "SearchInfo"}
        check_response = requests.get(BLAST_URL, params=check_params)

        if "Status=READY" in check_response.text:
            print("✅ BLAST computation completed!")
            break
        else:
            print("⏳ BLAST is still running...")
            time.sleep(10)

    # 3️⃣ Retrieve BLAST results in the selected format
    result_params = {"CMD": "Get", "RID": rid, **format_params}
    result_response = requests.get(BLAST_URL, params=result_params)

    output_text = result_response.text.strip()

    # 4️⃣ Debugging: Print raw output to check if the data is correct
    print("Raw BLAST output:")
    print(output_text)

    # 5️⃣ Process M8 Format for Display
    
    # 6️⃣ For other formats, display first 20 lines
    first_20_lines = "\n".join(output_text.splitlines()[:20])

    output_file = f"blast_results.{format_type.lower()}"
    with open(output_file, "w") as f:
        f.write(output_text)

    return first_20_lines, output_file


# Build the Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🔬 Online BLAST Query Tool (Gradio + NCBI API)")

    with gr.Row():
        seq_input = gr.Textbox(label="🔹 Enter DNA Sequence", placeholder="Enter a DNA sequence here", lines=3)
        format_dropdown = gr.Dropdown(label="📄 Output Format", choices=list(BLAST_FORMATS.keys()), value="")
        submit_btn = gr.Button("🚀 Run BLAST")

    output_display = gr.Textbox(label="📜 BLAST Output (first 20 lines)", interactive=False)
    download_btn = gr.File(label="⬇️ Download Results")

    submit_btn.click(run_blast, inputs=[seq_input, format_dropdown], outputs=[output_display, download_btn])

# Launch the Gradio app
demo.launch()
