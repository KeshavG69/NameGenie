from PIL import Image
from unstructured.partition.auto import partition
import tiktoken
import os
from pathlib import Path


def image_name(file_path):
    image = Image.open(file_path)

    if image.mode != "RGB":
        image = image.convert("RGB")

    prompt = "<CAPTION>"
    inputs = image_processor(text=prompt, images=image, return_tensors="pt")
    generated_ids = image_model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=1024,
        num_beams=3,
    )
    generated_text = image_processor.batch_decode(
        generated_ids, skip_special_tokens=False
    )[0]

    parsed_answer = image_processor.post_process_generation(
        generated_text, task=prompt, image_size=(image.width, image.height)
    )

    return parsed_answer[prompt].replace(" ", "_")


def text_name(file_path):
    encoding = tiktoken.get_encoding("cl100k_base")
    elements = partition(filename=file_path)
    word_content = ""
    for el in elements:
        word_content += str(el)

    num_tokens = len(encoding.encode(str(word_content)))

    while num_tokens > 5000:
        content_length = len(word_content)
        # Reduce the content by a certain ratio; here, reducing by 10%
        new_length = int(content_length * 0.90)
        word_content = word_content[:new_length]
        num_tokens = len(encoding.encode(word_content))

    messages = [
        {
            "role": "assistant",
            "content": "You are an expert in generating file names based on the content provided. Given the content of a text or image file, suggest a concise and descriptive file name that is no longer than 20 characters. Ensure the name captures the essence of the content without including any personal or sensitive information. Do not include the file extension; provide only the file name.",
        },
        {"role": "user", "content": word_content},
    ]
    text = text_tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    model_inputs = text_tokenizer([text], return_tensors="pt")

    generated_ids = text_model.generate(
        model_inputs.input_ids, max_new_tokens=20, temperature=0.7
    )
    generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = text_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    response = response.replace(" ", "_")
    first_period_index = response.find(".")

    # Extract text before the first period
    if first_period_index != -1:
        response = response[:first_period_index]
    else:
        response

    if '"' in response or "'" in response:
        response = response.replace('"', "").replace("'", "")
    return response


def change_file_name(old_file_name, response):
    path = Path(old_file_name)
    directory_name = str(Path(old_file_name).parent)
    file_extension = Path(old_file_name).suffix
    new_name = directory_name + "/" + response + file_extension
    os.rename(old_file_name, new_name)


def get_all_files(directory):
    directory_path = Path(directory)
    file_list = [str(file) for file in directory_path.glob("**/*") if file.is_file()]
    return file_list


def rename(directory_path):
    supported_formats = [
        ".docx",
        ".doc",
        ".odt",
        ".pptx",
        ".ppt",
        ".xlsx",
        ".csv",
        ".tsv",
        ".eml",
        ".msg",
        ".rtf",
        ".epub",
        ".html",
        ".xml",
        ".pdf",
        ".txt",
        ".md",
    ]
    img_supported_formats = [".jpg", ".jpeg", ".png", ".heic"]

    files = get_all_files(directory_path)
    for file in files:
        if Path(file).suffix.lower() in img_supported_formats:

            change_file_name(file, image_name(file))
            print(f"[SUCCESS] Renamed {file} successfully!! ")

        elif Path(file).suffix in supported_formats:

            change_file_name(file, text_name(file))
            print(f"[SUCCESS] Renamed {file} successfully!! ")

        else:
            print("[ERROR] FILE TYPE NOT SUPPORTED")
