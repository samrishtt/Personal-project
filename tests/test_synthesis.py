#!/usr/bin/env python
"""
Test the full synthesis API with parallel execution of multiple mock agents.
"""
import urllib.request
import urllib.parse
import json
import time

def test_synthesis():
    """Test the /api/run endpoint with mock agents."""
    
    # Test payload with multiple agents
    payload = {
        "query": "What is the most important factor in machine learning model success?",
        "debaters": ["Mock Skeptic", "Mock Optimist"],
        "judge": "Mock Judge",
        "fact_checker": "Mock Fact Checker",
        "adversarial": "Mock Challenger",
        "rounds": 2,
        "budget": 0.5,
        "temp": 0.7,
        "consensus_threshold": 0.55
    }
    
    # Encode payload
    data = json.dumps(payload).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        'http://localhost:5000/api/run',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print("=" * 70)
    print("TESTING PARALLEL SYNTHESIS WITH MOCK AGENTS")
    print("=" * 70)
    print(f"\nQuery: {payload['query']}")
    print(f"Agents: {len(payload['debaters'])} debaters + fact-checker + stress-tester + judge = 5 total")
    print(f"Rounds: {payload['rounds']}")
    print(f"Budget: ${payload['budget']}")
    
    # Send request and measure time
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            elapsed = time.time() - start_time
            
            print(f"\n✓ Synthesis completed in {elapsed:.2f}s")
            print(f"\nRESULTS:")
            print(f"  Rounds completed: {result['rounds_completed']}/{result['rounds_requested']}")
            print(f"  Total cost: ${result['total_cost']:.6f}")
            print(f"  Reason stopped: {result['stopped_reason']}")
            
            if result['rounds']:
                for round_data in result['rounds']:
                    print(f"\n  Round {round_data['round']}:")
                    print(f"    Responses: {len(round_data['responses'])} agents")
                    print(f"    Consensus: {round_data['consensus']:.1%}")
                    print(f"    Cost: ${round_data['round_cost']:.6f}")
                    
                    # Show agent names
                    agents = [r['agent'] for r in round_data['responses']]
                    print(f"    Agents: {', '.join(agents)}")
            
            print(f"\n✓ Judge/Synthesizer output generated")
            if result['judge']:
                print(f"  Model: {result['judge']['model']}")
                print(f"  Confidence: {result['judge']['confidence']:.0%}")
            
            if result['warnings']:
                print(f"\n⚠ Warnings ({len(result['warnings'])}):")
                for w in result['warnings']:
                    print(f"  - {w}")
            
            # Show final answer (first 300 chars)
            final_answer = result['final_answer']
            final = (final_answer[:300] + "...") if len(final_answer) > 300 else final_answer
            print(f"\nFinal Synthesized Answer Preview:")
            print(f"  {final}")
            
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error {e.code}")
        print(f"  {e.read().decode()}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == '__main__':
    test_synthesis()
