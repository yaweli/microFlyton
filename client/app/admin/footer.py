from tools.sql import *


def footer(data):

    current_page = data.get("rpage", data["s"].get("page", "dashboard"))
    g         = gen_data()
    pages_skip = g.get("pages_skip",[])
    for p in pages_skip:
        if current_page.startswith(p):
            return



    print(f"""
    <footer class="bg-dark text-center text-muted py-3 mt-5">
        <small>
            &copy; KIC &nbsp;&mdash;&nbsp; All rights reserved.
            &nbsp;|&nbsp;
            <a href="https://github.com/yaweli/microFlyton" target="_blank" rel="noopener">About Us</a>
        </small>
    </footer>
    """)
