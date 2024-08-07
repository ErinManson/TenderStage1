import requests
import pdfplumber
import os
import shutil
import pytesseract
from pdf2image import convert_from_path

# Function to download PDF
def download_pdf(pdf_url, output_path):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        response = requests.get(pdf_url, headers=headers, allow_redirects=True)
        if response.status_code == 200 and response.headers['Content-Type'] == 'application/pdf':
            with open(output_path, 'wb') as file:
                file.write(response.content)
            print("PDF downloaded successfully.")
        else:
            print(f"Failed to download PDF. Status code: {response.status_code}, Content-Type: {response.headers.get('Content-Type')}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_text(pdf_path):
    text = ""
    tables_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract text
                if page.extract_text():
                    text += page.extract_text() + "\n"

                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        row = [str(cell) if cell is not None else "" for cell in row]
                        tables_text += "\t".join(row) + "\n"
                    tables_text += "\n"
    except Exception as e:
        print(f"An error occurred while extracting data: {e}")
    return text

def extract_text_ocr(pdf_path):
    try:
        # Convert PDF to images with high resolution
        pages = convert_from_path(pdf_path, 300)
        
        # Iterate through all the pages stored above
        for i, page in enumerate(pages):
            print(f"Processing page {i+1}")
            image_path = f'page_{i}.jpg'
            page.save(image_path, 'JPEG')
            
            # Use Tesseract to do OCR on the image
            text = pytesseract.image_to_string(image_path)
            
            # Remove the image file after processing
            os.remove(image_path)
            
            # Check if the text contains the words "Rotary" or "Quantity"
            if "Rotary" in text or "Quantity" in text:
                return True
        
    except Exception as e:
        print(f"An error occurred while extracting text: {e}")
    
    return False

def main(pdf_url):

    # Download PDF from url and extract text into text variable
    pdf_path = 'downloaded_file.pdf'

    download_pdf(pdf_url, pdf_path)
    text = extract_text(pdf_path)
    #store text in .txt file
    f = open("downloaded_file.txt", "w")
    f.write(text)
    f.close()

    #separate text into lines to more easily manipulate
    text_list = text.splitlines()
    oldlen=len(text_list)

    #open a new file to store altered text
    f = open("test.txt", "w")
    #Loop through lines of text and make changes
    filtered_text=[]
    j=0
    header = ""
    kept = 0
    #loop through lines
    for i in text_list:
    #check if key characters are in text to keep
        #check if we are in table to enable not_kept tracking to prevent missing important lines
        if ("" not in i) and ("" not in i) and ("☐" not in i) :
            #if not check for quantity required
            if "Quantity Required" in i or ("QTY" in i) or ("Quant" in i):
                filtered_text.append("\n")
                filtered_text.append(header)
                entry=i.replace("_", "")
                for k in range(1,4):
                    if "_" in text_list[j+k]:
                        value=text_list[j+k]
                        value=value.replace("_","")
                        entry=entry+value
                filtered_text.append(entry)
                kept = 1 #because we kept set zero
            elif "Solicitation closes" in i or "Solicitation Closes" in i:
                header = header + "Solicitation closes: "
                for l in range(1,9):
                    if "on –" in text_list[j+l] or "at –" in text_list[j+l]:
                        header = header + "\n" + text_list[j+l]
                kept = 0 #dont set to 0 in this case becasue we don't think other important info will follow

            elif kept == 1 or kept == 2 or kept == 3:
                if ("table" not in i) and ("Table" not in i):
                    filtered_text.append(i)
                kept+=1
            else:
                #dont keep if not in table or if not_kept is too high
                #instead we set to zero and discard
                kept = 0

        else:
            #keep in check box found
            filtered_text.append(i)
            kept = 1
        j+=1
        
    for i in filtered_text:
        f.write(i)
        f.write("\n")
    f.close()

    shutil.copyfile("test.txt", "temp.txt")

    #read
    f = open("temp.txt", "r")
    data = f.read()
    f.close()
    box_replace = {
        "": "Y",
        "": "Y",
        "": "Y",
        "": "Y",
        "": "N",
        "☐": "N",
        "": "-",
        "": "->",
        "": ""
    }

    for i, j in box_replace.items():
        data = data.replace(i,j)

    f = open("temp.txt", "w")
    f.write(data)

    print(oldlen)
    print(len(filtered_text))
    # Delete the specified files
    files_to_delete = ['downloaded_file.pdf', 'downloaded_file.txt', 'test.txt']
    for file in files_to_delete:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass  # Ignore the error if the file does not exist
if __name__ == "__main__":
    main("https://canadabuys.canada.ca//sites//default//files//webform//tender_notice//42195//1000260139_rfp_en.pdf")
