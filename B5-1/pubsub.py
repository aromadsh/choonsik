from hash_map import HashMap
from doubly_linked_list import DoublyLinkedList
from stack_queue_deque import Queue
from dynamic_array import DynamicArray


class Subscriber:
    # 구독자별 메시지 큐와 채널 목록

    def __init__(self):
        self.messages = Queue()
        self.channels = HashMap()


class PubSub:
    # 채널을 통한 메시지 전달 시스템

    def __init__(self):
        self.channels = HashMap()
        self.subscribers = HashMap()

    # 특정 구독자를 채널에 등록
    def subscribe(self, channel, subscriber_id):
        sub = self.subscribers.get(subscriber_id)

        if sub is None:
            sub = Subscriber()
            self.subscribers.put(subscriber_id, sub)

        if sub.channels.contains(channel):
            return 0

        members = self.channels.get(channel)

        if members is None:
            members = DoublyLinkedList()
            self.channels.put(channel, members)

        node = members.insert_back(subscriber_id)
        sub.channels.put(channel, node)

        return 1

    # 채널의 구독을 해제
    def unsubscribe(self, channel, subscriber_id):
        sub = self.subscribers.get(subscriber_id)

        if sub is None or not sub.channels.contains(channel):
            return 0

        node = sub.channels.remove(channel)
        members = self.channels.get(channel)

        members.remove_node(node)

        if members.size() == 0:
            self.channels.remove(channel)

        return 1

    # 채널 구독자의 메시지 큐에 전달
    def publish(self, channel, message):
        members = self.channels.get(channel)

        if members is None:
            return 0

        count = 0
        current = members.head

        while current is not None:
            sub = self.subscribers.get(current.data)

            sub.messages.enqueue((channel, message))

            count += 1
            current = current.next

        return count

    # 구독자 큐에 쌓인 메시지를 모두 반환
    def receive(self, subscriber_id):
        sub = self.subscribers.get(subscriber_id)
        result = DynamicArray()

        if sub is None:
            return result

        while sub.messages.size() > 0:
            result.append(sub.messages.dequeue())

        return result
    