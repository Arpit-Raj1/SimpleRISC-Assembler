import streamlit as st
import tempfile

from assembler import init, look_for_loops_or_labels, assemble_line, remove_comments


def assemble_code(lines):
    init()
    look_for_loops_or_labels(lines)

    machine_code = []
    for line in lines:
        clean_line = remove_comments(line)
        if clean_line.strip() == "":
            continue
        machine_code_line = assemble_line(line)
        if machine_code_line and not machine_code_line.startswith("ERROR"):
            machine_code.append(machine_code_line)
        elif machine_code_line.startswith("ERROR"):
            machine_code.append(f"{line.strip()}  --> {machine_code_line}")
    return machine_code


def main():
    st.set_page_config(page_title="TinyRISC Assembler", layout="wide")
    st.title("🛠 TinyRISC Assembler")

    st.write(
        "Upload your `.asm` file or write code manually. You can also edit uploaded code before assembling."
    )

    uploaded_code = ""
    uploaded_file = st.file_uploader("📁 Upload Assembly File (.asm)", type=["asm"])

    if uploaded_file:
        uploaded_code = uploaded_file.read().decode("utf-8")

    # Text area for editing (whether user uploaded or writing new code)
    st.subheader("✍️ Edit or Write Assembly Code")
    code_area = st.text_area(
        "Assembly Code", value=uploaded_code, height=400, key="code_editor"
    )

    if st.button("▶️ Assemble Code"):
        if not code_area.strip():
            st.warning("Please upload or write some Assembly code first.")
            return

        lines = code_area.splitlines()

        try:
            machine_code = assemble_code(lines)

            st.success("✅ Assembly successful!")

            st.subheader("📄 Machine Code Output")
            output_text = "\n".join(machine_code)
            st.code(output_text, language="text")

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".mc") as f:
                f.write(output_text)
                f.seek(0)
                st.download_button(
                    "⬇️ Download .mc File", f.read(), file_name="output.mc"
                )

        except Exception as e:
            st.error(f"❌ Error during assembly: {e}")


if __name__ == "__main__":
    main()
