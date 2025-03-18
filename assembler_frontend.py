import streamlit as st
from io import BytesIO

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
            st.session_state["machine_code"] = (
                machine_code  # 🔥 Save machine code to session state
            )

            # Convert to binary
            binary_data = bytearray()
            for code_line in machine_code:
                if code_line.startswith("ERROR") or "-->" in code_line:
                    continue
                try:
                    byte_value = int(code_line, 2)
                    binary_data += byte_value.to_bytes(4, byteorder="big")
                except ValueError:
                    continue
            st.session_state["binary_data"] = (
                binary_data  # 🔥 Save binary data to session state
            )

            st.success("✅ Assembly successful!")

        except Exception as e:
            st.error(f"❌ Error during assembly: {e}")

    # Show machine code and download buttons AFTER assembly
    if "machine_code" in st.session_state:
        machine_code = st.session_state["machine_code"]
        output_text = "\n".join(machine_code)

        st.subheader("📄 Machine Code Output")
        st.code(output_text, language="text")

        mc_buffer = BytesIO(output_text.encode("utf-8"))
        st.download_button(
            "⬇️ Download .mc File",
            data=mc_buffer,
            file_name="output.mc",
            mime="text/plain",
        )

    if "binary_data" in st.session_state and st.session_state["binary_data"]:
        bin_buffer = BytesIO(st.session_state["binary_data"])
        st.download_button(
            "⬇️ Download .bin File",
            data=bin_buffer,
            file_name="output.bin",
            mime="application/octet-stream",
        )


if __name__ == "__main__":
    main()
