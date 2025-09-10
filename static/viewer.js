function xmlToTree(xmlNode) {{
    console.log('start...');
      const ul = document.createElement("ul");
      [...xmlNode.childNodes].forEach(node => {{
        if (node.nodeType === 1) {{
          const li = document.createElement("li");
          const tag = document.createElement("span");
          tag.className = "tag";
          tag.textContent = `<${{node.nodeName}}>`;
          li.appendChild(tag);

          if (node.attributes.length > 0) {{
            const attrs = Array.from(node.attributes).map(attr => `${{attr.name}}="${{attr.value}}"`).join(" ");
            const attrSpan = document.createElement("span");
            attrSpan.className = "text";
            attrSpan.textContent = " " + attrs;
            li.appendChild(attrSpan);
          }}

          if (node.childNodes.length > 0) {{
            li.appendChild(xmlToTree(node));
          }}

          const endTag = document.createElement("span");
          endTag.className = "tag";
          endTag.textContent = `</${{node.nodeName}}>`;
          li.appendChild(endTag);

          li.onclick = (e) => {{
            if (e.target === li || e.target === tag) {{
              li.classList.toggle("collapsed");
              e.stopPropagation();
            }}
          }};

          ul.appendChild(li);
        }} else if (node.nodeType === 3 && node.nodeValue.trim()) {{
          const li = document.createElement("li");
          li.className = "text";
          li.textContent = node.nodeValue.trim();
          ul.appendChild(li);
        }}
      }});

      return ul;
    }}

    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlString, "application/xml");

    const tree = xmlToTree(xmlDoc.documentElement);
    document.getElementById("xml-tree").appendChild(tree);
