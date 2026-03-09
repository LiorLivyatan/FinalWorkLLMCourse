"""Split Q21G-V4.pdf into chapters based on verified TOC."""

from pypdf import PdfReader, PdfWriter
import os

INPUT_PDF = "Q21G-V4.pdf"
OUTPUT_DIR = "chapters"
OFFSET = 26  # physical_page = printed_page + 26

# Chapters defined by (printed_start_page, filename, description)
# Each chapter ends just before the next one starts.
# Last chapter extends to end of document.
CHAPTERS = [
    (None,  "00_front_matter",                    "Front Matter (Title, TOC, Lists)"),
    (1,     "01_overview_Q21G_league",            "Ch1 - General Overview of Q21G League"),
    (27,    "02_architectural_principles",        "Ch2 - Architectural Principles for Agent"),
    (59,    "03_league_system_multi_agent",        "Ch3 - League System Multi-Agent Architecture"),
    (73,    "04_inter_agent_communication",        "Ch4 - Inter-Agent Communication Protocol"),
    (91,    "05_game_mechanisms",                  "Ch5 - Game Mechanisms"),
    (109,   "06_final_project_implementation",     "Ch6 - Final Project Implementation"),
    (131,   "07_administration",                   "Ch7 - Management and Administration"),
    (145,   "08_referee_game_management",          "Ch8 - Referee Game Management"),
    (167,   "09_appendix_A_gmail_oauth",           "Appendix A - Gmail OAuth Setup"),
    (171,   "10_appendix_B_protocol_messages",     "Appendix B - Protocol Messages Repository"),
    (183,   "11_appendix_C_data_model",            "Appendix C - System Data Model"),
    (211,   "12_appendix_D_player_db_schema",      "Appendix D - Player Agent DB Schema"),
    (231,   "13_appendix_E_gmail_api_traffic",     "Appendix E - Gmail API Traffic Analysis"),
    (241,   "14_ch10_id_conventions",              "Ch10 - ID Conventions"),
    (249,   "15_ch11_system_configuration",        "Ch11 - System Configuration"),
    (255,   "16_appendix_H_league_manager_arch",   "Appendix H - League Manager Architecture"),
    (261,   "17_appendix_I_gatekeeper_guide",      "Appendix I - GateKeeper Implementation Guide"),
    (269,   "18_appendix_J_sequence_diagrams",     "Appendix J - Message Sequence Diagrams"),
]

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    reader = PdfReader(INPUT_PDF)
    total_pages = len(reader.pages)
    print(f"Total physical pages in PDF: {total_pages}")

    for i, (printed_start, filename, description) in enumerate(CHAPTERS):
        # Determine physical start page (0-indexed for pypdf)
        if printed_start is None:
            # Front matter: physical pages 0 through OFFSET-1
            phys_start = 0
        else:
            phys_start = printed_start + OFFSET - 1  # convert to 0-indexed

        # Determine physical end page (0-indexed, inclusive)
        if i + 1 < len(CHAPTERS):
            next_printed_start = CHAPTERS[i + 1][0]
            if next_printed_start is None:
                phys_end = OFFSET - 1  # shouldn't happen since front matter is first
            else:
                phys_end = next_printed_start + OFFSET - 2  # page before next chapter
        else:
            phys_end = total_pages - 1  # last chapter goes to end

        # Special case: front matter ends at OFFSET-1
        if printed_start is None:
            phys_end = OFFSET - 1

        writer = PdfWriter()
        for page_idx in range(phys_start, phys_end + 1):
            writer.add_page(reader.pages[page_idx])

        output_path = os.path.join(OUTPUT_DIR, f"{filename}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)

        page_count = phys_end - phys_start + 1
        printed_range = f"pp. {printed_start}-{printed_start + page_count - 1}" if printed_start else "front matter"
        print(f"  {output_path:<60} ({page_count:>3} pages) - {description}")

    print(f"\nDone! {len(CHAPTERS)} files written to '{OUTPUT_DIR}/'")

if __name__ == "__main__":
    main()
