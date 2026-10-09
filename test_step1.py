from dynamic_array import DynamicArray
from doubly_linked_list import DoublyLinkedList


def test_dynamic_array():
    arr = DynamicArray(2)

    arr.append("A")
    arr.append("B")
    arr.append("C")

    assert arr.size() == 3
    assert arr.capacity == 4

    assert arr.get(0) == "A"
    assert arr.get(2) == "C"

    arr.set(1, "X")
    assert arr.get(1) == "X"

    removed = arr.remove(0)

    assert removed == "A"
    assert arr.size() == 2
    assert arr.get(0) == "X"

    print("DynamicArray TEST PASS")


def test_linked_list():
    linked = DoublyLinkedList()

    node_a = linked.insert_front("A")
    node_b = linked.insert_back("B")
    node_c = linked.insert_back("C")

    assert linked.size() == 3

    linked.move_to_front(node_c)

    assert linked.head is node_c
    assert linked.tail is node_b

    linked.remove_node(node_a)

    assert linked.size() == 2

    linked.remove_front()
    linked.remove_back()

    assert linked.size() == 0
    assert linked.head is None
    assert linked.tail is None

    print("DoublyLinkedList TEST PASS")


if __name__ == "__main__":
    test_dynamic_array()
    test_linked_list()
    print("STEP 1 ALL TESTS PASS")