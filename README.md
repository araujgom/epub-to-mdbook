# ePub to MDBook

I consider myself a "book hacker". I love reading across various formats and experimenting with new typographies and layouts. While I generally prefer my Kindle, the technical books — rich with complex structures and images — often don't render well on e-ink screens.

I've also noticed a gap between the simplicity of Markdown-based documentation tools and the complexity of the ePub format. For example, [mdBook](https://rust-lang.github.io/mdBook/) lets you create beautiful websites or books from Markdown files. However, it doesn't support ePub files, which are the most common format for technical books.

That’s why I created this project — a simple tool that converts ePub files into mdBook projects. This allows me to read my technical books on a visually appealing website with excellent layout, typography, and easy navigation through chapters and sections. The project also have rooms for improvements that I will be working on in the future.

I hope you enjoy it! Feedback and contributions are always welcome.

**Disclaimer:** This project was created for personal use only and does not support piracy; it’s intended for ePub files you own and have the proper rights to read.

## Prerequisites

Before running this project, ensure that you have the following installed on your system:

- **Python (3.12 or higher recommended):**
  Verify your installation by running:
  ```bash
  python --version
  ```
- **uv (Python Packaging Tool):**
  [uv](https://astral.sh/blog/uv) is used to manage dependencies and create isolated virtual environments. If you haven’t installed uv yet, you can install it via the standalone installer:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  Alternatively, you may install via pipx:
  ```bash
  pipx install uv
  ```
- **mdBook:**
  This project converts an ePub file to an mdBook project. Make sure you have mdBook installed on your system. Refer to [mdBook's installation guide](https://rust-lang.github.io/mdBook/guide/installation.html) for instructions.
- **Other Dependencies:**
  All other Python dependencies are managed through the `pyproject.toml` file. (uv will automatically handle dependency resolution and lock file generation.)

## Usage

Once you have the prerequisites installed, follow these steps to run the project:

1. **Clone the Repository and Set Up the Environment**

   Clone the project repository and change into its directory. Then, use uv to synchronize the project’s environment (uv will create a virtual environment and install all required dependencies automatically):
   ```bash
   git clone https://github.com/araujgom/epub-to-mdbook
   cd epub-to-mdbook
   uv sync
   ```
   (Alternatively, if you prefer to use uv’s convenience for running commands without manual activation, you can skip manually activating the virtual environment.)

2. **Run the Conversion Script**

   The main script accepts an input ePub file and optional arguments. Instead of using the regular Python interpreter, you can run the command through uv to ensure that the virtual environment is used. For example:
   ```bash
   uv run main.py path/to/input.epub --output output_directory --heading_style ATX
   ```
   This command will:
   - Convert the ePub file into an mdBook project in the specified output directory.
   - Print conversion details such as title, authors, and the number of chapters processed.
   - Automatically attempt to build the mdBook by running:
     ```bash
     mdbook build
     ```
   - If the build is successful, the script then serves the mdBook by running:
     ```bash
     mdbook serve
     ```

3. **Access the Generated mdBook**

   After running the conversion, open your web browser and navigate to the URL provided by the `mdbook serve` command (typically something like `http://localhost:3000`) to view your converted book.