# Args :
# - Path to the image file

import sys
args = sys.argv
if len(args) != 2:
    print("Invalid Argument Count : ", len(args))
    sys.exit()

prompt = (
    "Convert this equation image to LaTex"
    "Use $$ equations, you can use multiple if you needed"
    "If you need to align = signs for example, use \\begin{align*}, careful as it already acts as $$, you can't put it inside $$"
    "Don't necessarily follow the style of the image, I prefer something that looks good rather than an exact copy, for example if there are small integral signs, make them big anyways"
    "For styled letters use \\mathcal{} (only when needed of course)"
    "Only output the LaTex code, no explanation, and put it as plain text, no ```latex."
)

from google import genai
from PIL import Image

client = None
with open("latextool/gemini_key.txt") as f:
    client = genai.Client(api_key=f.read())

img = Image.open(args[1])

response = client.models.generate_content(model="gemini-2.5-flash", contents=[
    img,
    prompt
])

print(response.text)