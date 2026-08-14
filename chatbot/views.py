from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import NewsUsers, Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

from .ai import ask_ai


@api_view(['GET', 'POST'])
def conversations(request):

    if request.method == 'GET':
        conversations = Conversation.objects.all()
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ConversationSerializer(data=request.data)

        if serializer.is_valid():
            conversation = serializer.save()
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET', 'POST'])
def messages(request):

    if request.method == 'GET':
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            message = serializer.save()
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
def chatbot(request):

    question = request.data.get('question')

    if not question:
        return Response(
            {'error': 'Question is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    answer = ask_ai(question)

    return Response({
        'question': question,
        'answer': answer
    })