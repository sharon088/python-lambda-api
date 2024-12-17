import wikipediaapi
import os

def append_wikipedia_summary(topic):
    """ Fetches the summary of a Wikipedia topic and appends it to `./outputs/wikipedia.txt` """
    try:
        wiki = wikipediaapi.Wikipedia(
            language="en",
            user_agent="MyWikiSummaryScript/1.0 (https://example.com; contact@example.com)"
        )

        page = wiki.page(topic)
        if not page.exists():
            print(f"The topic '{topic}' does not exist on Wikipedia.")
            return
        
        summary = page.summary
        output_dir = "./outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, "wikipedia.txt")
        with open(output_file, "a", encoding="utf-8") as file:
            file.write(f"\nTopic: {topic}\n")
            file.write(f"{summary}\n")
            file.write("=" * 80 + "\n")       
        print(f"Successfully added summary of '{topic}' to '{output_file}'.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python wiki_to_file.py <topic>")
    else:
        append_wikipedia_summary(sys.argv[1])