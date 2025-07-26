# Gradio Eval Server Template

A comprehensive, Hugging Face-compliant template for creating evaluation servers with leaderboard functionality using Gradio. This template provides a complete solution for hosting AI model evaluation benchmarks with user authentication, rate limiting, and automated scoring.

**Ready to host your AI evaluation benchmark?** This template provides everything you need to create a professional, secure, and user-friendly evaluation server with comprehensive leaderboard functionality.

## 🚀 Features

### Core Functionality
- **Evaluation Server**: Upload and evaluate model predictions against ground truth data
- **Public Leaderboard**: Real-time ranking of submissions with customizable sorting
- **User Authentication**: Secure login system using Gradio's OAuth integration
- **Rate Limiting**: Configurable submission limits and cooldown periods
- **Submission Management**: Optional saving of submissions with privacy controls
- **Easily Configurable**: Simply toggle features, e.g., disable leaderboard or eval functionality.

### Security & Access Control
- **OAuth Authentication**: Secure user login with Hugging Face accounts
- **Rate Limiting System**: 
  - Daily submission limits per user
  - Total submission limits per user
  - Minimum interval between submissions
  - Persistent state tracking across server restarts
- **Privacy Controls**: Option to submit privately without saving to leaderboard
- **Input Validation**: JSON validation and submission format checking

### User Experience
- **Real-time Feedback**: Immediate scoring and quota updates
- **Quota Tracking**: Visual display of remaining daily and total submissions
- **Submission Cleaning**: Optional automatic cleaning of raw model responses
- **Responsive Interface**: Clean, intuitive Gradio-based UI

### Technical Features
- **Modular Architecture**: Separated concerns with dedicated modules
- **Configurable Settings**: Easy customization via `config.py`
- **Persistent Storage**: Automatic saving of submissions and rate limiter state
- **Error Handling**: Comprehensive error messages and validation
- **Extensible Design**: Easy to modify evaluation logic and scoring metrics

## 📁 Project Structure

```
gradio-eval-server-template/
├── app.py                 # Main Gradio application
├── config.py             # Configuration settings (Tweak to your liking!)
├── eval_utils.py         # Evaluation logic and utilities (Implement your own!)
├── rate_limiter.py       # Rate limiting implementation 
├── ground_truth.json     # Your ground truth data for evaluation (Path is configurable)
└── submissions/          # Optional: directory for storing submissions (Path is configurable)
```

## ⚙️ Configuration

All settings are easily configurable in `config.py`:

```python
# File paths
GROUND_TRUTH = "ground_truth.json"           # Path to ground truth data
SUB_DIR = "./submissions"                    # Submission storage directory

# Rate limiting
RATE_LIMIT_MIN_INT_SEC = 10                  # Minimum seconds between submissions (0 = unlimited)
MAX_TOTAL_SUBMISSIONS_PER_USER = 40          # Total submissions per user (0 = unlimited)
MAX_SUBMISSIONS_PER_USER_PER_DAY = 10        # Daily submissions per user (0 = unlimited)

# Submission handling
SAVE_SUBMISSIONS = True                      # Save submissions to leaderboard
SAVE_SUBMISSION_PREDICTIONS = True           # Save prediction data with submissions

# Interface options
SHOW_LEADERBOARD = True                      # Display public leaderboard
SHOW_EVAL_SERVER = True                      # Display evaluation interface
```

## 🛠️ Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/paulgavrikov/gradio-eval-server-template.git
   cd gradio-eval-server-template
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your evaluation**:
   - Update `ground_truth.json` with your benchmark data
   - Modify `eval_utils.py` to implement your evaluation logic
   - Adjust settings in `config.py` as needed

4. **Run the server**:
   ```bash
   python app.py
   ```

### or deploy to Hugging Face Spaces!
1. Push your code to a GitHub repository
2. Create a new Space on Hugging Face
3. Select Gradio as the SDK
4. Point to your repository
5. The Space will automatically deploy your eval server

## 📊 Evaluation System

### Ground Truth Format
Store your benchmark data in `ground_truth.json`. The format depends on your specific evaluation needs.

### Custom Evaluation Logic
Implement your evaluation metrics in `eval_utils.py`:

```python
def evaluate_submission(preds, ground_truth) -> dict:
    # Implement your evaluation logic here
    # Return a dictionary of metric_name: score pairs
    return {"accuracy": 0.95, "f1_score": 0.87}
```

### Submission Cleaning
Optionally implement cleaning logic for raw model outputs:

```python
def clean_submission(preds):
    # Clean and normalize predictions
    # e.g., extract answers from long-form responses
    return cleaned_preds
```

## 🏆 Leaderboard System

The leaderboard automatically:
- Displays all public submissions
- Sorts by configurable metrics
- Shows submission identifiers and scores
- Updates in real-time after new submissions

### Customization
Modify the `get_leaderboard()` function in `app.py` to:
- Change sorting criteria
- Add additional columns
- Implement custom ranking logic
- Filter submissions
- Add static (non-submission based) leaderboard

## 🔐 Authentication & Security

### OAuth Integration
- Uses Hugging Face OAuth for secure authentication
- No need to manage user accounts or passwords
- Automatic user identification and tracking

### Rate Limiting Features
- **Daily Limits**: Prevent spam with daily submission caps
- **Total Limits**: Control overall participation
- **Cooldown Periods**: Enforce minimum time between submissions
- **Persistent State**: Rate limits survive server restarts

### Privacy Controls
- **Private Submissions**: Submit without saving to leaderboard
- **Optional Prediction Storage**: Choose whether to save prediction data

## 🔧 Customization Guide

### Implement Your Metrics
1. Modify `evaluate_submission()` in `eval_utils.py`
2. Add your metric calculation logic
3. Return the new metric in the score dictionary

### Changing the UI
- Modify the Gradio interface in `app.py`
- Add new tabs, components, or functionality
- Customize styling and layout

### Database Integration
- Replace file-based storage with a database
- Modify submission saving logic in `app.py`
- Update leaderboard querying accordingly


## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- New features
- Documentation improvements
- Performance optimizations

## 📄 License

This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License - see the LICENSE file for details.


