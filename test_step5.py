from stack_queue_deque import Stack, Queue, Deque
from binary_tree import TreeNode, BinaryTree
from bst import BinarySearchTree
from pubsub import PubSub
from mini_redis import MiniRedis
from cli import execute


def values(arr):
    return [
        arr.get(i)
        for i in range(arr.size())
    ]


def test_collections():
    s = Stack()
    s.push(1)
    s.push(2)

    assert (
        s.peek(), s.pop(), s.pop(), s.pop()
    ) == (2, 2, 1, None)

    q = Queue()
    q.enqueue(1)
    q.enqueue(2)

    assert (
        q.peek(), q.dequeue(),
        q.dequeue(), q.dequeue()
    ) == (1, 1, 2, None)

    d = Deque()
    d.append_left(2)
    d.append_left(1)
    d.append_right(3)

    assert (
        d.pop_left(), d.pop_right(),
        d.pop_left(), d.size()
    ) == (1, 3, 2, 0)

    print("Stack/Queue/Deque TEST PASS")


def test_tree():
    tree = BinaryTree(
        TreeNode(
            "A",
            TreeNode(
                "B",
                TreeNode("D"),
                TreeNode("E")
            ),
            TreeNode("C")
        )
    )

    assert values(tree.preorder()) == [
        "A", "B", "D", "E", "C"
    ]

    assert values(tree.inorder()) == [
        "D", "B", "E", "A", "C"
    ]

    assert values(tree.postorder()) == [
        "D", "E", "B", "C", "A"
    ]

    assert values(tree.levelorder()) == [
        "A", "B", "C", "D", "E"
    ]

    print("BinaryTree traversals TEST PASS")


def test_bst():
    tree = BinarySearchTree()

    for n in (8, 3, 10, 1, 6, 14, 4, 7, 13):
        assert tree.insert(n)

    assert not tree.insert(3)
    assert tree.search(6)
    assert not tree.search(99)

    assert values(tree.inorder()) == [
        1, 3, 4, 6, 7, 8, 10, 13, 14
    ]

    assert tree.delete(1)
    assert tree.delete(14)
    assert tree.delete(3)
    assert tree.delete(8)

    assert values(tree.inorder()) == [
        4, 6, 7, 10, 13
    ]

    assert tree.size() == 5

    print("BST insert/search/delete TEST PASS")


def test_pubsub():
    p = PubSub()

    assert p.subscribe("news", "alice") == 1
    assert p.subscribe("news", "alice") == 0
    assert p.subscribe("news", "bob") == 1
    assert p.subscribe("sports", "alice") == 1

    assert p.publish("news", "hello") == 2
    assert p.publish("sports", "goal") == 1

    assert values(p.receive("alice")) == [
        ("news", "hello"),
        ("sports", "goal")
    ]

    assert values(p.receive("bob")) == [
        ("news", "hello")
    ]

    assert p.unsubscribe("news", "bob") == 1
    assert p.publish("news", "again") == 1

    assert values(p.receive("alice")) == [
        ("news", "again")
    ]

    assert p.receive("bob").size() == 0

    print("PubSub TEST PASS")


def test_cli():
    db = MiniRedis()
    p = PubSub()

    assert execute(
        db, "SUBSCRIBE news alice", p
    ) == "(integer) 1"

    assert execute(
        db, "SUBSCRIBE news bob", p
    ) == "(integer) 1"

    assert execute(
        db, 'PUBLISH news "Hello World"', p
    ) == "(integer) 2"

    assert execute(
        db, "RECEIVE alice", p
    ) == '1. ["news", "Hello World"]'

    assert execute(
        db, "RECEIVE alice", p
    ) == "(empty array)"

    assert execute(
        db, "UNSUBSCRIBE news bob", p
    ) == "(integer) 1"

    assert execute(
        db, "PUBLISH news next", p
    ) == "(integer) 1"

    assert execute(
        db, "SET k v", p
    ) == "OK"

    assert execute(
        db, "GET k", p
    ) == '"v"'

    print("CLI integration TEST PASS")


if __name__ == "__main__":
    test_collections()
    test_tree()
    test_bst()
    test_pubsub()
    test_cli()

    print("STEP 5 ALL TESTS PASS")