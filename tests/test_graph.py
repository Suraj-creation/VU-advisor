"""End-to-end LangGraph loop with a scripted stand-in for the Azure model (no credentials needed)."""
import json

from langchain_core.messages import AIMessage, ToolMessage

from advisor import graph


class ScriptedLLM:
    """First call: request a tool. Second call: answer citing the returned source plus one fabricated id."""

    def __init__(self):
        self.calls = []

    def invoke(self, msgs):
        self.calls.append(msgs)
        if not isinstance(msgs[-1], ToolMessage):
            return AIMessage(content="", tool_calls=[{"name": "lookup_courses", "id": "t1",
                                                      "args": {"batch": 2025, "course": "Machine Learning"}}])
        sid = next(iter(json.loads(msgs[-1].content)["sources"]))  # cite what the tool just returned
        return AIMessage(content=f"Machine Learning (DATA301) is 2-0-4, 4 credits [{sid}, S42]; DATA206 does not exist in the data [S42].")  # grouped + fabricated


def test_graph_turn_grounds_and_verifies(monkeypatch):
    fake = ScriptedLLM()
    monkeypatch.setattr(graph, "llm", lambda bind_tools=True: fake)
    monkeypatch.setattr(graph, "_GRAPH", None)
    out = graph.ask("L-T-P of Machine Learning for 2025?", thread_id="t-test")
    assert "[S1]" in out["answer"] and "[S42]" not in out["answer"]
    assert out["flags"]["removed_citations"] == ["S42"] and out["flags"]["tools"] == ["lookup_courses"]
    assert out["sources"][0]["citation"].endswith("Sem_Spread_2025 › AI16:AO16")
    assert "No student profile is selected" in fake.calls[0][0].content  # system prompt reflects missing profile
    # second turn on the same thread keeps history and continues source numbering
    out2 = graph.ask("And for 2024?", thread_id="t-test")
    assert out2["flags"]["cited"] == ["S2"] and len(fake.calls[2]) > 3  # new id; history (turn 1) was sent
