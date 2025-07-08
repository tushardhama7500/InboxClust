
# RUN it on google colab to download the flowchart of this project:

# Install Graphviz if not installed
!pip install graphviz

from graphviz import Digraph

# Initialize Digraph
dot = Digraph(comment='Email Intelligence System Flowchart')
dot.attr(rankdir='TB', size='8', bgcolor='white', fontname='Helvetica')

# Style dictionary
style_main = {"shape": "box", "style": "filled", "color": "lightblue", "fontname": "Helvetica"}
style_sub = {"shape": "box", "style": "filled", "color": "lightgrey", "fontname": "Helvetica"}

# Main steps
dot.node('A', '📥 Fetch Inbox\nfetch_emails.py', **style_main)
dot.node('B', '🚫 Fetch Spam\nfetch_spam_emails.py', **style_main)
dot.node('C', '🧹 Clean Spam\nSpamCleaner.py', **style_main)
dot.node('D', '📊 Cluster Emails\ncluster_emails.py', **style_main)
dot.node('E', '🧠 Manual Labeling\nconfig.py', **style_main)
dot.node('F', '🏷️ Assign Labels\nfind_label.py', **style_main)
dot.node('G', '🧩 Merge Datasets\nmerger_csv.py', **style_main)
dot.node('H', '📈 Train Model\nspam_detector.py', **style_main)
dot.node('I', '🤖 Telegram Notifier\nemail_notifier_tele.py', **style_main)
dot.node('J', '💬 Telegram Actions\ntelegram_api.py', **style_main)
dot.node('K', '⚙️ Email Actions\nemail_utils.py', **style_main)
dot.node('L', '🌐 Language Switch\n/language command', **style_main)

# Group spam flow
with dot.subgraph(name='cluster_spam') as s:
    s.attr(rank='same')
    s.node('B')
    s.node('C')

# Inbox → Clustering path
dot.edge('A', 'D', label='Inbox to Clusters')
dot.edge('B', 'C', label='Clean spam')
dot.edge('D', 'E', label='Manual check')
dot.edge('E', 'F', label='Apply Labels')
dot.edge('F', 'G', label='Merge clean + labeled')
dot.edge('C', 'G', label='Merge cleaned spam')

# Model & Notifier
dot.edge('G', 'H', label='Use merged data')
dot.edge('H', 'I', label='Predict & Notify')

# Telegram Bot Actions
dot.edge('I', 'J', label='Send buttons')
dot.edge('J', 'K', label='Perform Actions')
dot.edge('J', 'L', label='Change Language')

# Render and display
dot.render('email_intelligence_flowchart', format='png', cleanup=False)
dot

