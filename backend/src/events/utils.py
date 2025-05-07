from fastapi import HTTPException
from fpdf import FPDF
from src.config import Config
import jwt
import io


class TicketService:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)

    def generate_ticket_token(self, ticket_data: dict):
        payload = {
            "ticket_id": ticket_data["ticket_id"],
            "event_id": ticket_data["event_id"],
            "user_id": ticket_data["user_id"],
            "first_name": ticket_data["first_name"],
            "last_name": ticket_data["last_name"],
            "ticket_type": ticket_data["ticket_type"],
            "event_name": ticket_data["event_name"],
            "event_date": ticket_data["event_date"].isoformat(),
            "event_location": ticket_data["event_location"]
        }

        token = jwt.encode(payload, Config.TICKET_TOKEN_SECRET, algorithm=Config.TICKET_TOKEN_ALGORITHM)
        return token
    
    def verify_ticket_token(self, token: str):
        # While checking in the event, we can use this function to verify the ticket token
        try:
            payload = jwt.decode(token, Config.TICKET_TOKEN_SECRET, algorithms=[Config.TICKET_TOKEN_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Ticket token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid ticket token")

    def generate_ticket_and_save(self, token: str):
        ticket_data = self.verify_ticket_token(token)

        self.pdf.set_font("Arial", size=16, style="B")
        self.pdf.cell(200, 10, txt=ticket_data["event_name"], ln=True, align="C")
        self.pdf.set_font("Arial", size=12)
        self.pdf.cell(200, 10, txt=f"Date: {ticket_data['event_date']}", ln=True, align="C")
        self.pdf.cell(200, 10, txt=f"Location: {ticket_data['event_location']}", ln=True, align="C")

        self.pdf.set_font("Arial", size=12, style="B")
        self.pdf.cell(200, 10, txt="Ticket ID:", ln=True, align="C")
        self.pdf.set_font("Arial", size=12)
        self.pdf.cell(200, 10, txt=ticket_data["ticket_id"], ln=True, align="C")

        self.pdf.set_font("Arial", size=12, style="B")
        self.pdf.cell(200, 10, txt="Ticket Type:", ln=True, align="C")
        self.pdf.set_font("Arial", size=12)
        self.pdf.cell(200, 10, txt=ticket_data["ticket_type"], ln=True, align="C")

        self.pdf.set_font("Arial", size=12, style="B")
        self.pdf.cell(200, 10, txt="Ticket Holder:", ln=True, align="C")
        self.pdf.set_font("Arial", size=12)
        self.pdf.cell(200, 10, txt=f"{ticket_data['first_name']} {ticket_data['last_name']}", ln=True, align="C")

        # Create an in-memory PDF file
        pdf_bytes = io.BytesIO()
        pdf_content = self.pdf.output(dest='S').encode('latin1')  # Generate PDF as bytes
        pdf_bytes.write(pdf_content)
        pdf_bytes.seek(0)  # Set cursor to start of the file

        return pdf_bytes
