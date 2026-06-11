import json
import os
from pathlib import Path
from src.schemas import BehavioralLog, DomainData, UserProfile
from src.engine import evaluate_domain

def load_mock_data(filepath: str) -> UserProfile:
    with open(filepath, 'r') as f:
        raw_data = json.load(f)
        
    domains = {}
    for domain_name, domain_content in raw_data['domains'].items():
        logs = [
            BehavioralLog(
                timestamp=log['timestamp'],
                action=log['action'],
                magnitude=log['magnitude']
            ) for log in domain_content.get('behavioral_logs', [])
        ]
        domains[domain_name] = DomainData(
            self_talk=domain_content.get('self_talk', []),
            behavioral_logs=logs
        )
        
    return UserProfile(user_id=raw_data['user_id'], domains=domains)

def main():
    # Setup paths
    base_dir = Path(__file__).parent.parent
    input_path = base_dir / "data" / "mock_input.json"
    results_dir = base_dir / "results"
    output_path = results_dir / "worked_examples.json"

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    print(f"Loading data for candidate from {input_path}...")
    profile = load_mock_data(input_path)
    
    results = []
    # Evaluate over an assumed 3-day window based on our mock data
    evaluation_days = 3 
    
    for domain_name, domain_data in profile.domains.items():
        print(f"Evaluating domain: {domain_name.upper()}")
        output = evaluate_domain(domain_name, domain_data, evaluation_days)
        results.append(output.__dict__)
        print(f" -> Result: {output.classification} (Uncertainty: {output.uncertainty_score})\n")

    # Save outputs
    with open(output_path, 'w') as f:
        json.dump({
            "user_id": profile.user_id,
            "domain_results": results
        }, f, indent=2)
        
    print(f"Success! Results saved to {output_path}")

if __name__ == "__main__":
    main()