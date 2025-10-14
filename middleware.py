from fastapi.middleware.cors import CORSMiddleware

def configure_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173","*"],
        # allow_origins=["http://localhost:3000", "https://event-hall-booking.vercel.app","http://localhost:8081","exp://192.168.1.4:8081","http://192.168.1.4:8081"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
