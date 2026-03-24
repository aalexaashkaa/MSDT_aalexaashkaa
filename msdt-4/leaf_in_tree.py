import sys
import logging
import os

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(os.path.join('logs', "l4_logs.log"), encoding="utf-8")]
)
logger = logging.getLogger("l4_logs")


class Node:
    """Класс, представляющий узел дерева."""

    def __init__(self, value):
        """Инициализация узла"""

        self.value = value
        self.children = []


    def add_child(self, child_node):
        """Добавление дочернего узла"""

        self.children.append(child_node)


class Tree:
    """Класс, представляющий узел дерева."""

    def __init__(self, root = None):
        """Инициализация дерева"""

        self.root = root
        self.nodes = {}
    
    
    def get_node(self, value):
        """Получение узла по значению"""

        if value in self.nodes:
            return self.nodes[value]
        else:
            return None
    
    
    def get_parent(self, value):
        """Получение списка родителей узла"""

        res = []
        for node in self.nodes.values():
            if value in node.children:
                res.append(node)
        return res
        

    def visualization(self):
        """Отображение всех узлов"""

        for i in self.nodes.keys():
            print(f'Узел: {i}. Дети: {[str(j.value) + " " for j in self.nodes[i].children]}')


    def get_count_leafs(self):
        """Подсчет листьев"""

        res = 0
        for node in self.nodes.values():
            if node.children == []:
                res += 1
        return res


def parsing(f):
    """Парсинг файла"""

    tree = Tree()
    logger.info(f"Start parsing file: {f.name}")

    for line_num, line in enumerate(f, 1):
    
        if ':' not in line:
            logger.error(f"Line {line_num}: Missing ':' symbol")
            raise ValueError("Строка не содержит символ ':'")
        
        if ' ' in line:
            logger.error(f"Line {line_num}: Contains spaces")
            raise ValueError("Строка содержит пробелы")
        
        st = line.strip().split(':')
        head = st[0]
        tail = st[1].split(',')

        if not head:
            logger.error(f"Line {line_num}: Empty node name before ':'")
            raise ValueError("Пустое имя узла перед символом ':'")

        if tree.get_node(head) is None:
            new_node = Node(head)
            tree.nodes[head] = new_node
            logger.debug(f"Node created in tree: '{new_node.value}'")
    
        else:
            new_node = tree.get_node(head)
        
        
        if tail[0] != '':
            for i in tail:
                if tree.get_node(i) == None:
                    child_node = Node(i)
                    tree.nodes[i] = child_node
                    logger.debug(f"Node created in tree: '{child_node.value}'")
                else:
                    child_node = tree.get_node(i)

                new_node.add_child(child_node)

        if len(new_node.children) != len(set(new_node.children)):
            logger.error(f"Line {line_num}: Non-unique name")
            raise ValueError("Присутствие узлов с неуникальными названиями")
    
    #После парсинга определяется корень дерева
    for node in tree.nodes.values():
        parents = tree.get_parent(node)

        if len(parents) > 1:
            logger.error(f"Node '{node.value}' has multiple parents")
            raise ValueError("Присутствие узлов с двумя или более родителями")

        elif len(parents) == 0 and tree.root == None:
            tree.root = node
            logger.info(f"Root node identified: '{tree.root.value}'") 

        elif len(parents) == 0 and tree.root != None:
            logger.error(f"Multiple root nodes: {tree.root.value} and {node.value}")
            raise ValueError("Присутствие более одного корневого узла")
        
    if tree.root == None:
        logger.error(f"No root node")
        raise ValueError("Отсутствие корневого узла")
    return tree


def run(file_name):
    """Запуск обработки файла"""

    logger.info(f"Attempting to open file: {file_name}")

    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            logger.info(f"File opened successfully: {file_name}")

            new_tree = parsing(file)
            logger.debug(f"File content parsed successfully: {file_name}")

            leaf_count = new_tree.get_count_leafs()
            print(f'Количество листьев в данном дереве: {leaf_count}')
            logger.info(f"Leaf count:  '{leaf_count}'")

            logger.info(f"Closing file: {file_name}")
            return leaf_count
        
    except FileNotFoundError:
        print(f"Файл {file_name} не найден")
        logger.error(f"File not found: {e}")
        raise

    except ValueError as e:
        print(f"Ошибка в формате данных: {e}", file=sys.stderr)
        logger.error(f"Validation error: {e}")
        raise

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        print(f'Используется: python leaf_in_tree.py {file_name}')
        try:
            run(file_name)
        except (ValueError, FileNotFoundError) as e:
            sys.exit(1)
    else:
        print("Укажите имя файла: python leaf_in_tree.py <filename>", file=sys.stderr)
        sys.exit(1)
