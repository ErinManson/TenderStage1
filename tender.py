import get_id, get_links, update_score
import pdf_converter
import shutil
import os
from urllib.parse import unquote, urlparse
import manual_review
import json_create
import json_push

""" STEP 1 gets posts with pdf links, scores them using the bart model on how 
relevant they are then sends back a list of post ids and a list of pdfs for postings 
where the score was greater than 4 """

def separate_urls(input_list):
    postings = []
    for item in input_list:
        postings.append(item)
    return postings
def main():
    # Example usage
    update_score.main()
    ids =  get_id.sql_main()
    postings = get_links.sql_main()

    """ STEP 2 looping through each post from STEP 1 pdfConverter converts the pdf urls to 
    readable text then looks for chair builder pages inside said text. If chair builders 
    were found it will be stored in a text file containing all chair builders for that post """

    #loop through posts
    j=0
    for post in postings:
        j+=1
        i=0
        print("post " + str(j-1))
        #loop through urls scanning each until we get a hit for a chair builder page in a text format for now
        found_builder = "No"
        #while we havent found builder pages or we have reached a stopping point
        while found_builder == "No" and found_builder != "Stop":
            for url in post:
                i+=1
                pdf_converter.main(str(url))
                #after converting we read the final text file and see if it contains more than 20 lines of useful info
                with open("temp.txt", 'r') as fp:
                    lines = len(fp.readlines())
                    if lines >= 20:
                        found_builder = "Yes"
                        postname = str(ids[j-1]) + "-" + str(i) + "builder.txt"
                        shutil.copyfile("temp.txt", postname)
                    os.remove("temp.txt")

            # If no builder is found after all URLs are processed
            if found_builder == "No":
                # Send post back through for OCR checking for key words
                for url in post:
                    if pdf_converter.extract_text_ocr(url):
                        found_builder = "Yes"
                        print("Builder detected, post needs manual review")
                        manual_review.update_manual_check(ids[j - 1])
                        found_builder = "Man"
                        break
    #if we loop through all urls set to stop
            if found_builder == "No":
                found_builder = "Stop"
            elif found_builder == "Stop":
                print("No chair builder page found for this post!")
            elif (found_builder == "Yes"):
                print("Chair builder page found see .txt file")
            else:
                print("possible builder, needs manual review")
            i+=1

    directory = r"Posts"

    # Iterate over files in directory
    for name in os.listdir(directory):
        # Open file
        with open(os.path.join(directory, name)) as f:
            # Read content of file
            file_text = f.read()
            chair_builders = file_text.split("\n\n")
            # Remove short segments
            chair_builders = [i.strip() for i in chair_builders if len(i.strip()) > 10]

            # Split and save into multiple files
            for index, chunk in enumerate(chair_builders):
                new_filename = os.path.join(directory, f"{os.path.splitext(name)[0]}-{index + 1}.txt")
                with open(new_filename, "w") as new_file:
                    new_file.write(chunk + "\n")

        # Delete the original file
        os.remove(os.path.join(directory, name))


    json_create.main()
    json_push.main()
    print("Job Done")


main()
