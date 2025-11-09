from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from google import genai
import logging
from .models import ChatSession, Message
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

# Initialize Gemini API client
try:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    client = None

DEFAULT_REPLY = "Sorry, I couldn't generate a response right now."

@login_required
def chat_view(request, session_id=None):
    # Create new chat session if no session_id or ?new=true
    if not session_id or request.GET.get('new') == 'true':
        session = ChatSession.objects.create(title=f"Chat {Message.objects.count() + 1}")
        return redirect('chat', session_id=session.id)

    session = get_object_or_404(ChatSession, id=session_id)

    if request.method == 'POST':
        msg_text = request.POST.get('message', '').strip()
        if not msg_text or len(msg_text) > 1000:
            return JsonResponse({'error': 'Message must be 1-1000 characters.'}, status=400)

        # Save user message
        Message.objects.create(text=msg_text, sender='user', session=session)

        # Prepare AI reply
        ai_text = DEFAULT_REPLY
        if client:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Answer briefly and accurately: {msg_text}"
                )
                if response.text.strip():
                    ai_text = ' '.join(response.text.strip().split()[:100])
            except Exception as e:
                logger.error(f"Gemini API error: {e}")

        # Save bot message
        bot = Message.objects.create(text=ai_text, sender='bot', session=session)

        # Return only the bot message (not all)
        history = ChatSession.objects.order_by('-updated_at')[:settings.CHAT_HISTORY_LIMIT]
        history_data = [{'id': h.id, 'title': h.title} for h in history]

        return JsonResponse({
            'messages': [{'id': bot.id, 'text': bot.text, 'sender': bot.sender}],
            'history': history_data
        })

    # GET request
    messages = session.messages.all()
    history = ChatSession.objects.order_by('-updated_at')[:settings.CHAT_HISTORY_LIMIT]

    return render(request, 'chat.html', {
        'session': session,
        'messages': messages,
        'history': history
    })
