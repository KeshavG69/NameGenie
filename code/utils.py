from PIL import Image
from unstructured.partition.auto import partition
import tiktoken
import os
from pathlib import Path


def image_name(file_path):
    """
    Generate a descriptive name for an image file based on its content.

    This function takes the path to an image file, processes the image, and uses a pre-trained model
    to generate a caption for the image. The generated caption is then formatted to create a
    filename-friendly string.

    Parameters:
    ----------
    file_path : str
        The file path to the input image. Supported formats include JPEG, PNG, and other standard image formats.

    Returns:
    -------
    str
        A string representing a formatted name for the image, with spaces replaced by underscores.

    Steps:
    ------
    1. **Open the image**: The function opens the image from the provided file path using PIL's Image module.

    2. **Convert to RGB**: If the image is not in RGB mode, it converts the image to RGB format to ensure compatibility
       with the image processing model.

    3. **Prepare inputs**: It constructs a prompt for captioning and processes the image along with the prompt using
       the `image_processor` to prepare the inputs for the model.

    4. **Generate captions**: The function invokes the `image_model` to generate text based on the processed image and
       prompt using beam search to create more coherent outputs.

    5. **Decode generated text**: The generated IDs are decoded back to text format while retaining any special tokens.

    6. **Post-process generation**: The decoded text undergoes a post-processing step to ensure it meets the specific
       requirements of the task and is formatted based on the original image dimensions.

    7. **Format the output**: Finally, the generated caption is returned, with spaces replaced by underscores to create
       a suitable filename.

    Example Usage:
    --------------
    >>> name = image_name("path/to/image.jpg")
    >>> print(name)
    'A_descriptive_name_based_on_image_content'

    Notes:
    ------
    - Ensure that the necessary dependencies such as PIL and the specific image processor/model
      are properly imported and initialized before calling this function.
    - The function assumes that `image_processor` and `image_model` are globally defined and initialized
      instances of your chosen image processing and model classes.
    """
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
    """
    Generate a concise and descriptive file name based on the content of a text file.

    This function processes the content of the specified text file, tokenizes it, and uses a pre-trained model
    to generate a short, descriptive file name that captures the essence of the content. The generated name
    is formatted to replace spaces with underscores and is limited to 20 characters.

    Parameters:
    ----------
    file_path : str
        The file path to the input text file. The function reads and processes the content to generate an appropriate file name.

    Returns:
    -------
    str
        A string representing a formatted file name, with spaces replaced by underscores and truncated
        before any periods.

    Steps:
    ------
    1. **Token Encoding**: Retrieves the token encoding using the `tiktoken` library for the specified encoding scheme ("cl100k_base").

    2. **Content Extraction**: Partitions the file's content using a custom `partition` function and concatenates
       the elements into a single string.

    3. **Token Count Check**: Counts the number of tokens in the content and reduces the length of the content
       if the token count exceeds 5000, trimming the content by 10% in each iteration.

    4. **Message Preparation**: Constructs a message list containing instructions for generating a file name
       and the content of the file.

    5. **Template Application**: Applies a chat template to format the messages using a `text_tokenizer`.

    6. **Model Input Generation**: Processes the text and prepares it as input for the model.

    7. **File Name Generation**: Generates a file name using the `text_model` and retrieves the output
       IDs while excluding the input tokens.

    8. **Response Decoding**: Decodes the generated IDs to retrieve the final output text, replacing spaces with
       underscores.

    9. **Formatting**: Trims the response at the first period (if present) and removes any quotation marks.

    Example Usage:
    --------------
    >>> name = text_name("path/to/textfile.txt")
    >>> print(name)
    'A_concise_name_for_file'

    Notes:
    ------
    - Ensure that the necessary dependencies such as `tiktoken` and the specific tokenizer/model
      are properly imported and initialized before calling this function.
    - The function assumes that `partition`, `text_tokenizer`, and `text_model` are globally defined and initialized
      instances of your chosen partitioning and modeling classes.
    """
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
    """
    Change the name of a file based on the provided response.

    This function renames a specified file by constructing a new name using the response provided,
    while maintaining the original file's directory and extension.

    Parameters:
    ----------
    old_file_name : str
        The current file path of the file to be renamed, including the file name and extension.

    response : str
        The new file name (without extension) that will be used to rename the file. Spaces in the response
        will not be modified, but it is recommended to format it as needed for best results.

    Returns:
    -------
    None
        The function renames the file in place and does not return any value.

    Steps:
    ------
    1. **Extract the Directory**: Retrieves the directory path of the old file using `Path`.

    2. **Get File Extension**: Extracts the file extension from the old file name to ensure the new name
       retains the original file format.

    3. **Construct New Name**: Creates the new file name by combining the directory path, the response
       (new name), and the original file extension.

    4. **Rename the File**: Uses `os.rename` to rename the old file to the new file name.

    Example Usage:
    --------------
    >>> change_file_name("path/to/old_file.txt", "new_file_name")
    # This renames 'old_file.txt' to 'new_file_name.txt' in the same directory.

    Notes:
    ------
    - Ensure that the `old_file_name` exists and that `response` is a valid name that adheres to file naming
      conventions.
    - The function will overwrite any existing file with the new name without warning.
    """

    directory_name = str(Path(old_file_name).parent)
    file_extension = Path(old_file_name).suffix
    new_name = directory_name + "/" + response + file_extension
    os.rename(old_file_name, new_name)


def get_all_files(directory):
    """
    Retrieve a list of all files in a specified directory and its subdirectories.

    This function scans the given directory recursively and collects the paths of all files found,
    returning them as a list of strings.

    Parameters:
    ----------
    directory : str
        The path to the directory to scan for files. The function will search through all
        subdirectories as well.

    Returns:
    -------
    list of str
        A list containing the paths of all files found in the specified directory and its subdirectories.

    Steps:
    ------
    1. **Create a Path Object**: Converts the input directory string to a `Path` object for easy manipulation.

    2. **File Listing**: Uses the `glob` method with the pattern `**/*` to recursively find all files
       in the directory and its subdirectories.

    3. **Filter and Collect Files**: Filters the results to include only files (excluding directories)
       and converts their paths to strings.

    Example Usage:
    --------------
    >>> files = get_all_files("path/to/directory")
    >>> print(files)
    # This prints a list of all file paths in the specified directory.

    Notes:
    ------
    - Ensure that the specified directory exists and is accessible.
    - This function will return an empty list if no files are found.
    """
    directory_path = Path(directory)
    file_list = [str(file) for file in directory_path.glob("**/*") if file.is_file()]
    return file_list


def rename(directory_path):
    """
    Rename files in a specified directory based on their content.

    This function scans the provided directory for supported file formats, and renames each file
    by generating a new name based on its content using dedicated functions for text and image files.
    Supported file types for renaming include various document formats and image formats.

    Parameters:
    ----------
    directory_path : str
        The path to the directory containing the files to be renamed. The function will process
        all files within this directory and its subdirectories.

    Returns:
    -------
    None
        The function renames files in place and does not return any value.

    Supported Formats:
    ------------------
    - Document formats: .docx, .doc, .odt, .pptx, .ppt, .xlsx, .csv, .tsv, .eml, .msg, .rtf,
      .epub, .html, .xml, .pdf, .txt, .md.
    - Image formats: .jpg, .jpeg, .png, .heic.

    Steps:
    ------
    1. **Define Supported Formats**: Lists of supported document and image formats are defined.

    2. **Get All Files**: Calls the `get_all_files` function to retrieve all files in the specified directory.

    3. **File Renaming**: Iterates through the list of files:
       - If the file is an image (based on its extension), it calls `image_name(file)` to generate a new name
         and renames the file using `change_file_name`.
       - If the file is a supported document format, it calls `text_name(file)` to generate a new name
         and renames the file similarly.
       - If the file type is unsupported, it logs an error message.

    Example Usage:
    --------------
    >>> rename("path/to/directory")
    # This processes all supported files in the specified directory and renames them accordingly.

    Notes:
    ------
    - Ensure that the necessary functions `get_all_files`, `change_file_name`, `image_name`, and
      `text_name` are defined and imported before calling this function.
    - The function will print success or error messages for each file processed.
    - It is recommended to back up the directory before running this function to avoid unintentional data loss.

    """
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
    files_name = [Path(file).stem for file in files]

    for file in files:
        if Path(file).suffix.lower() in img_supported_formats:
            original_name = Path(file).stem
            output=image_name(file)
            counter=1
            original_output = output
            while output in files_name and output != original_name:
              output = f"{original_output}_{counter}"
              counter += 1
            files_name.append(output)
            change_file_name(file,output)
            print(f"[SUCCESS] Renamed {file} successfully!! ")
        elif Path(file).suffix in supported_formats:
            original_name = Path(file).stem
            output=text_name(file)

            counter=1
            original_output = output
            while output in files_name and output != original_name:
                output = f"{original_output}_{counter}"
                counter += 1
            files_name.append(output)
            change_file_name(file,output)
            print(f"[SUCCESS] Renamed {file} successfully!! ")
        else:
            print("[ERROR] FILE TYPE NOT SUPPORTED")
