"""
Service layer for VoiceEmotionRAG
Orchestrates backend modules and business logic
"""

import time
from typing import Dict, List
from dataclasses import dataclass

from backend.emotion import detect_emotions
from backend.rag import retrieve
from backend.llm import generate
from backend.speech import transcribe
from observability.metrics import compute_grounding_score, estimate_hallucination_risk


@dataclass
class ProcessingResult:
    """Result from processing user input"""
    response: str
    emotion: Dict
    metrics: Dict


class VoiceEmotionService:
    """Main service for processing voice/text input"""
    
    @staticmethod
    def process_text(text: str) -> ProcessingResult:
        """
        Process text input through the full pipeline:
        1. Detect emotion
        2. Retrieve relevant documents
        3. Generate response
        4. Calculate metrics
        """
        start_time = time.time()
        
        # Step 1: Emotion detection
        emotion_results = detect_emotions(text)
        emotion_scores = {item['label']: item['score'] for item in emotion_results}
        
        # Step 2: Build emotion context
        top_emotion = emotion_results[0]
        emotion_context = f"User feels {top_emotion['label']} ({top_emotion['score']:.2f})"
        
        # Step 3: Retrieve documents
        rag_start = time.time()
        documents = retrieve(
            query=text,
            emotion_context=emotion_context,
            k=3
        )
        rag_latency = int((time.time() - rag_start) * 1000)
        
        # Step 4: Generate response
        llm_result = generate(
            user_text=text,
            emotion_context=emotion_context,
            retrieved_docs=documents
        )
        
        # Step 5: Calculate metrics
        total_latency = int((time.time() - start_time) * 1000)
        retrieval_scores = [doc['score'] for doc in documents]
        grounding_score = compute_grounding_score(retrieval_scores)
        
        # Map emotion labels to standardized emotion names
        emotion_label_map = {
            'sadness': 'sadness',
            'joy': 'joy',
            'love': 'joy',
            'fear': 'fear',
            'surprise': 'surprise',
            'anger': 'anger',
            'disgust': 'disgust',
            'neutral': 'neutral',
        }
        
        # Initialize all emotions to 0
        emotion_data = {
            'fear': 0.0,
            'surprise': 0.0,
            'anger': 0.0,
            'joy': 0.0,
            'sadness': 0.0,
            'neutral': 0.0,
            'disgust': 0.0,
        }
        
        # Fill in the emotion scores
        for label, score in emotion_scores.items():
            mapped_label = emotion_label_map.get(label, label)
            if mapped_label in emotion_data:
                emotion_data[mapped_label] = score
        
        # Build result
        return ProcessingResult(
            response=llm_result['text'],
            emotion={
                **emotion_data,
                'top_emotion': emotion_label_map.get(top_emotion['label'], top_emotion['label']),
                'top_score': top_emotion['score'],
            },
            metrics={
                'latency_ms': llm_result.get('latency_ms', 0),
                'tokens_out': llm_result['tokens'],
                'total_latency_ms': total_latency,
                'rag_latency_ms': rag_latency,
                'grounding': grounding_score,
                'hallucination': 1.0 - grounding_score,
                'llm_provider': llm_result.get('provider', 'unknown'),
            }
        )
    
    @staticmethod
    def transcribe_audio(file_path: str) -> str:
        """Transcribe audio file to text"""
        return transcribe(file_path)
