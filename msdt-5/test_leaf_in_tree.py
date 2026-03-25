import pytest
import leaf_in_tree
from io import StringIO

def test_duplicate_children():
    """Тест на дублирующиеся дочерние узлы"""
    content = StringIO("A:B,B\nB:\n")
    with pytest.raises(ValueError, match="Присутствие узлов с неуникальными названиями"):
        leaf_in_tree.parsing(content)

def test_multiple_parents():
    """Тест на узел с двумя родителями"""
    content = StringIO("A:B\nC:B\nB:\n")
    with pytest.raises(ValueError, match="Присутствие узлов с двумя или более родителями"):
        leaf_in_tree.parsing(content)

def test_no_root():
    """Тест без корневого узла"""
    content = StringIO("A:B\nB:A\n")
    with pytest.raises(ValueError, match="Отсутствие корневого узла"):
        leaf_in_tree.parsing(content)

def test_missing_colon():
    """Тест без символа ':'"""
    content = StringIO("A B\nB:A\n")
    with pytest.raises(ValueError, match="Строка не содержит символ ':'"):
        leaf_in_tree.parsing(content)

def test_empty_name():
    """Тест с отсутствием имени узла"""
    content = StringIO(":B\nB:A\n")
    with pytest.raises(ValueError, match="Пустое имя узла перед символом ':'"):
        leaf_in_tree.parsing(content)

def test_contains_spaces():
    """Тест с пробелами"""
    content = StringIO("A: B\nB :C\n")
    with pytest.raises(ValueError, match="Строка содержит пробелы"):
        leaf_in_tree.parsing(content)

def test_multiple_root():
    """Тест с несколькими корнями"""
    content = StringIO("A:B\nB:C\nD:E\nE:F\n")
    with pytest.raises(ValueError, match="Присутствие более одного корневого узла"):
        leaf_in_tree.parsing(content)

def test_visualization(capsys): 
    """Тест визуализации дерева"""
    content = StringIO("A:B,C\nB:D\nC:\nD:\n") 
    tree = leaf_in_tree.parsing(content) 
    tree.visualization() 
    captured = capsys.readouterr() 
    expected_output = ( "Узел: A. Дети: ['B ', 'C ']\n" 
                       "Узел: B. Дети: ['D ']\n" 
                       "Узел: C. Дети: []\n" 
                       "Узел: D. Дети: []\n" ) 
    assert captured.out == expected_output

def test_without_data():
    """Тест с несуществующим файлом"""
    file_name = 'test_file_1.txt'
    with pytest.raises(FileNotFoundError, match=f"No such file or directory: '{file_name}"):
        result = leaf_in_tree.run(file_name)

# Использование параметризированного тестирования
@pytest.mark.parametrize("content, expected_leafs", [
    ("A:\n", 1),
    ("A:B\nB:\n", 1),
    ("A:B,C\nB:\nC:\n", 2),
    
    ("A:B,C\nB:D,E\nC:F,G\nD:\nE:\nF:\nG:\n", 4),
    ("A:B,C\nB:D\nC:\nD:\n", 2),
    ("Root:Left,Right\nLeft:\nRight:\n", 2),
    
    ("A:B\nB:C\nC:D\nD:\n", 1),
    ("A:B,C\nB:D\nC:E\nD:F\nE:\nF:\n", 2),
])

def test_valid_trees_parametrized(content, expected_leafs):
    """Параметризованный тест для валидных деревьев"""
    content_io = StringIO(content)
    tree = leaf_in_tree.parsing(content_io)
    assert tree.get_count_leafs() == expected_leafs

# Тесты с использованием фикстур
@pytest.fixture
def data_file(tmp_path):
    """Фикстура, создающая файл с данными для проверки функции run()."""
    content = "A:B,C\nB:D\nC:E\nD:F\nE:\nF:\n"
    
    data_file = tmp_path / "sample_data.txt"
    data_file.write_text(content, encoding="utf-8")
    return data_file

def test_with_data(data_file):
    """Тест с использованием конкретного файла."""
    result = leaf_in_tree.run(data_file)
    assert result == 2

@pytest.fixture
def incorrect_data_file(tmp_path):
    """
    Фикстура, создающая файл с некорректными
    данными для проверки функции run().
    """
    content = "A B\nB:A\n"
    
    data_file = tmp_path / "sample_data.txt"
    data_file.write_text(content, encoding="utf-8")
    return data_file

def test_with_incorrect_data(incorrect_data_file):
    """Тест с использованием некорректного файла."""
    with pytest.raises(ValueError, match="Строка не содержит символ ':'"):
        leaf_in_tree.run(incorrect_data_file)
    
