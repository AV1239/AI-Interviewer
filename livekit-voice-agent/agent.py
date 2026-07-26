#import fal_client
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentServer, AgentSession, Agent, inference, room_io, TurnHandlingOptions
from livekit.plugins import ai_coustics, langchain, openai, cartesia, deepgram, noise_cancellation, silero, hedra
    

from graph import create_workflow
from PIL import Image
load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=
        "You are a professional interviewer conducting a job interview. " 
        "The LangGraph workflow will drive the conversation flow. " 
        "Be conversational, professional, and engaging throughout the interview process."
        )

server = AgentServer()

@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: agents.JobContext):
    lg_llm = langchain.LLMAdapter(graph=create_workflow())
    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=lg_llm,
        tts=inference.TTS(
            model="cartesia/sonic-3",
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        ),
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
        ),
    )
     
    avatar_image = Image.open("./Interviewer.png")
        
    # avatar = hedra.AvatarSession(
    #   avatar_image=avatar_image,
    # )
    
    #await avatar.start(session, room=ctx.room)
   
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=ai_coustics.audio_enhancement(model=ai_coustics.EnhancerModel.QUAIL_VF_S),
            ),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)