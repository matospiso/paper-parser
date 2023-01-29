import argparse
import re

import PyPDF2 as p2

parser = argparse.ArgumentParser()

parser.add_argument(
    "--path",
    help="Path to the PDF file",
    type=str,
    default="test_inputs/input.pdf",
)
parser.add_argument(
    "--output", help="Path to the output file", type=str, default="output.txt"
)
parser.add_argument(
    "--width", help="Width of the output text in characters", type=int, default=60
)  # best: 50-75

TEST_P = "test_inputs/Embarrassingly Shallow Autoencoders for Sparse Data.pdf"


def fix_letters(text: str) -> str:
    # fix letters f,t,T
    for c in "ftT":
        text = text.replace(f"/{c}_", c)
    # fix .sc
    for c in "abcdefghijklmnopqrstuvwxyz":
        text = text.replace(f"/{c}.sc", c.upper())
    return text


def parse_text(text: str, args: argparse.Namespace) -> str:
    def fix_newlines(text: str) -> str:
        # remove word hyphenation
        text = text.replace("-\n", "")
        # remove line breaks in mid-sentence after comma
        text = text.replace(",\n", "\n")
        # extract titles
        text = re.sub(
            r"(\s+)([0-9A-Z]+ ([0-9A-Z]+ )*[0-9A-Z]+)",
            "\n" + r"\2".strip() + "\n",
            text,
        )
        # remove line breaks in mid-sentence
        text = re.sub(r"(\b[a-zA-Z]+\b)\n([a-zA-Z]+\b)", r"\1 \2", text)
        return text

    def split_into_lines(text: str, max_width: int) -> str:
        words = text.split(" ")
        lines = []
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > max_width:
                lines.append(line.strip())
                line = ""
            line += word + " "
        lines.append(line)
        return "\n".join(lines)

    text = fix_newlines(text)

    text_lines = text.split("\n")
    text_lines = [line.strip() for line in text_lines]
    text_lines = [line for line in text_lines if line != ""]

    text = ""
    for line in text_lines:
        if len(line) > args.width:
            line = split_into_lines(line, args.width)
        text += line + "\n"
    return text


def main():
    args = parser.parse_args()
    pdf = p2.PdfReader(open(args.path, "rb"))

    parsed_pages = []

    for i in range(len(pdf.pages)):
        page = pdf.pages[i]
        extracted_page_text = page.extract_text()
        fixed_text = fix_letters(extracted_page_text)
        parsed_page = parse_text(fixed_text, args)
        parsed_pages.append(parsed_page)

    with open(args.output, "w") as f:
        for page in parsed_pages:
            f.write(page)
            f.write("\n\n")


if __name__ == "__main__":
    main()
