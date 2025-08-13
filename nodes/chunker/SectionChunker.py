import re

class SectionChunker:
    def __init__(self):
        pass

    def chunk_by_section(self, document_text):
        """
        Divide un documento Markdown in una lista di dizionari, basandosi
        sui marcatori '\n## ' e '\n### '.

        Args:
            document_text (str): Il testo del documento Markdown.

        Returns:
            list: Una lista di dizionari. Ogni dizionario rappresenta un capitolo
                  e le sue sezioni.
        """
        document_text = "\n" + document_text.strip()
        pattern = r"\n(##\s+|###\s+)"
        parts = re.split(pattern, document_text)
        
        if parts[0].strip() == "":
            parts = parts[1:]
        
        results = []
        current_chapter_dict = {}
        
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                marker = parts[i].strip()
                content = parts[i+1].strip()

                title_match = re.match(r'([0-9\.]+)\s+(.*)', content.splitlines()[0])
                
                if marker == '##':
                    if current_chapter_dict:
                        results.append(current_chapter_dict)
                    
                    current_chapter_dict = {}
                    
                    if title_match:
                        number = title_match.group(1).replace('.', '_')
                        title = title_match.group(2).strip()
                        key = f"{number}_{title}"
                        current_chapter_dict[key] = content
                    else:
                        key = content.splitlines()[0].replace(' ', '_')
                        current_chapter_dict[key] = content

                elif marker == '###' and current_chapter_dict:
                    if title_match:
                        number = title_match.group(1).replace('.', '_')
                        title = title_match.group(2).strip()
                        key = f"{number}_{title}"
                        current_chapter_dict[key] = content
                    else:
                        key = content.splitlines()[0].replace(' ', '_')
                        current_chapter_dict[key] = content
        
        if current_chapter_dict:
            results.append(current_chapter_dict)

        return results

    def __call__(self, document_text):
        return self.chunk_by_section(document_text)