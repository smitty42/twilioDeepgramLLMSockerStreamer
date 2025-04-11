import anthropic

client = anthropic.Anthropic()

class LLM:

    def __init__(self, from_number, call_sid):
        self.from_number = from_number
        self.call_sid = call_sid
        self.prompt = None

    def query_model(self, user_prompt):
        raise Exception("query_model not implemented for this class.")

    def post_process_response(self, turn_response=None):
        raise Exception("post_process_response not implemented for this class.")

    def query(self, user_prompt="I have a toothache"):
        raise Exception("query not implemented for this class.")


class AnthropicLLMConversation(LLM):
    system = """
    You area voice bot that has conversation with people about Fyodor
    Dostoevsky's work, "The Brothers Karamazov". You should try to answer
    whatever question people have about this book, and if they don't have
    questions or haven't read the book, you should convince them to read it.

    Try to keep you're response down to no more than five or so sentences. And
    don't bother with fancy formatting, remember that this is a voice
    conversation.
    """

    def query_model(self, user_prompt, conversation_history):
        messages = conversation_history
        next_turn = {"role": "user", "content": [{"type": "text", "text": user_prompt}]}
        messages.append(next_turn)

        turn_response_stream = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0,
            system=self.system,
            messages=messages,
            stream=True,
        )

        for event in turn_response_stream:
            yield event
