import os

from gitignore_parser import parse_gitignore


def find_scripts(root):
    try:
        ignore = parse_gitignore(os.path.join(root, '.scignore'))
    except FileNotFoundError:
        def ignore(_):
            return False

    def _find_scripts(dir_path):
        res = []
        for entry in os.scandir(dir_path):
            entry: os.DirEntry
            node = {'name': entry.name, 'path': os.path.relpath(entry.path, root)}
            if entry.name.startswith('.') or ignore(entry.path):
                continue

            if entry.is_dir():
                children = _find_scripts(entry.path)
                if not children:
                    continue
                node.update(children=children)

            res.append(node)

        res = sorted(res, key=lambda x: 'children' not in x)
        return res

    return _find_scripts(root)


if __name__ == '__main__':
    import pprint

    d = os.path.join(os.path.dirname(__file__), 'scripts')
    pprint.pprint(list(find_scripts(d)))
