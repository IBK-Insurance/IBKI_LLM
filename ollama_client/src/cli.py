import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
import os
import sys
from typing import Optional

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ollama_client import OllamaClient

app = typer.Typer(help="Ollama API 클라이언트 CLI")
console = Console()

@app.command()
def chat(
    model: str = typer.Option("gemma3", help="사용할 모델 이름"),
    session_id: str = typer.Option("default", help="대화 세션 ID"),
):
    """대화형 채팅 인터페이스"""
    client = OllamaClient()
    
    console.print(Panel.fit(
        "[bold blue]Ollama API 클라이언트[/bold blue]\n"
        f"모델: [green]{model}[/green]\n"
        f"세션 ID: [green]{session_id}[/green]\n"
        "종료하려면 'exit' 또는 'quit'를 입력하세요.",
        title="채팅 시작",
        border_style="blue"
    ))
    
    while True:
        user_input = Prompt.ask("\n[bold blue]사용자[/bold blue]")
        
        if user_input.lower() in ["exit", "quit"]:
            console.print("\n[bold red]채팅을 종료합니다.[/bold red]")
            break
        
        try:
            response = client.generate(
                prompt=user_input,
                model=model,
                session_id=session_id
            )
            
            console.print("\n[bold green]어시스턴트[/bold green]")
            console.print(Markdown(response))
        except Exception as e:
            console.print(f"[bold red]오류 발생:[/bold red] {str(e)}")

@app.command()
def list_models():
    """사용 가능한 모델 목록 표시"""
    client = OllamaClient()
    
    try:
        models = client.list_models()
        
        console.print(Panel.fit(
            "\n".join([f"- {model['name']}" for model in models]),
            title="사용 가능한 모델",
            border_style="blue"
        ))
    except Exception as e:
        console.print(f"[bold red]오류 발생:[/bold red] {str(e)}")

@app.command()
def pull_model(
    model_name: str = typer.Argument(..., help="다운로드할 모델 이름")
):
    """모델 다운로드"""
    client = OllamaClient()
    
    try:
        console.print(f"[bold blue]모델 '{model_name}' 다운로드 중...[/bold blue]")
        result = client.pull_model(model_name)
        console.print(f"[bold green]모델 '{model_name}' 다운로드 완료![/bold green]")
    except Exception as e:
        console.print(f"[bold red]오류 발생:[/bold red] {str(e)}")

@app.command()
def delete_model(
    model_name: str = typer.Argument(..., help="삭제할 모델 이름")
):
    """모델 삭제"""
    client = OllamaClient()
    
    try:
        console.print(f"[bold blue]모델 '{model_name}' 삭제 중...[/bold blue]")
        result = client.delete_model(model_name)
        console.print(f"[bold green]모델 '{model_name}' 삭제 완료![/bold green]")
    except Exception as e:
        console.print(f"[bold red]오류 발생:[/bold red] {str(e)}")

if __name__ == "__main__":
    app() 