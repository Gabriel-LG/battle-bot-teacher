#!/usr/bin/env python3
"""
BattleBot Teacher GUI
A graphical interface for controlling BattleBot robots via micro:bit serial interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import json
import os
from typing import Optional


class BattleBotGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BattleBot Teacher Control")
        self.root.geometry("600x600")
        self.serial_port: Optional[serial.Serial] = None
        
        # Load player names from config (in same directory as script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(script_dir, "battlebot_config.json")
        self.player_names = self.load_config()
        
        self.create_widgets()
        self.refresh_ports()
        
    def load_config(self) -> dict:
        """Load player names from config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Save player names to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.player_names, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Serial Port Selection Frame
        port_frame = ttk.LabelFrame(self.root, text="Serial Connection", padding=10)
        port_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(port_frame, text="Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_combo = ttk.Combobox(port_frame, width=30, state="readonly")
        self.port_combo.grid(row=0, column=1, padx=5)
        
        self.btn_refresh = ttk.Button(port_frame, text="Refresh", command=self.refresh_ports)
        self.btn_refresh.grid(row=0, column=2, padx=5)
        
        self.btn_connect = ttk.Button(port_frame, text="Connect", command=self.connect)
        self.btn_connect.grid(row=0, column=3, padx=5)
        
        self.btn_disconnect = ttk.Button(port_frame, text="Disconnect", command=self.disconnect)
        self.btn_disconnect.grid(row=0, column=4, padx=5)
        
        self.connection_status = ttk.Label(port_frame, text="Not Connected", foreground="red")
        self.connection_status.grid(row=1, column=0, columnspan=5, pady=5)
        
        # Global Controls Frame
        global_frame = ttk.LabelFrame(self.root, text="Global Controls", padding=10)
        global_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_mute = ttk.Button(global_frame, text="Mute All", command=lambda: self.send_command("mute,1"), 
                  width=20)
        self.btn_mute.grid(row=0, column=0, padx=5, pady=5)
        
        self.btn_unmute = ttk.Button(global_frame, text="Unmute All", command=lambda: self.send_command("mute,0"),
                  width=20)
        self.btn_unmute.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_stop = ttk.Button(global_frame, text="Stop All Motors", command=lambda: self.send_command("stop,1"),
                  width=20)
        self.btn_stop.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_enable = ttk.Button(global_frame, text="Enable All Motors", command=lambda: self.send_command("stop,0"),
                  width=20)
        self.btn_enable.grid(row=1, column=1, padx=5, pady=5)
        
        # Battle Controls Frame
        battle_frame = ttk.LabelFrame(self.root, text="Battle Setup", padding=10)
        battle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Player 1
        ttk.Label(battle_frame, text="Player 1:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(battle_frame, text="Robot ID:").grid(row=1, column=0, sticky=tk.W, padx=(20, 5))
        self.player1_id = ttk.Spinbox(battle_frame, from_=0, to=15, width=10, command=lambda: self.load_player_name(1))
        self.player1_id.set(0)
        self.player1_id.grid(row=1, column=1, sticky=tk.W, pady=2)
        self.player1_id.bind("<KeyRelease>", lambda e: self.load_player_name(1))
        self.player1_id.bind("<FocusOut>", lambda e: self.load_player_name(1))
        
        ttk.Label(battle_frame, text="Name:").grid(row=2, column=0, sticky=tk.W, padx=(20, 5))
        self.player1_name = ttk.Entry(battle_frame, width=25)
        self.player1_name.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=2)
        self.player1_name.bind("<FocusOut>", lambda e: self.on_player_name_change(1))
        self.player1_name.bind("<KeyRelease>", lambda e: self.on_player_name_change(1))
        
        # Load saved name for player 1 (without updating buttons yet)
        robot_id = self.player1_id.get()
        if robot_id in self.player_names:
            self.player1_name.insert(0, self.player_names[robot_id])
        else:
            self.player1_name.insert(0, f"Player {robot_id}")
        
        # Player 2
        ttk.Label(battle_frame, text="Player 2:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(15, 5))
        
        ttk.Label(battle_frame, text="Robot ID:").grid(row=4, column=0, sticky=tk.W, padx=(20, 5))
        self.player2_id = ttk.Spinbox(battle_frame, from_=0, to=15, width=10, command=lambda: self.load_player_name(2))
        self.player2_id.set(1)
        self.player2_id.grid(row=4, column=1, sticky=tk.W, pady=2)
        self.player2_id.bind("<KeyRelease>", lambda e: self.load_player_name(2))
        self.player2_id.bind("<FocusOut>", lambda e: self.load_player_name(2))
        
        ttk.Label(battle_frame, text="Name:").grid(row=5, column=0, sticky=tk.W, padx=(20, 5))
        self.player2_name = ttk.Entry(battle_frame, width=25)
        self.player2_name.grid(row=5, column=1, columnspan=2, sticky=tk.W, pady=2)
        self.player2_name.bind("<FocusOut>", lambda e: self.on_player_name_change(2))
        self.player2_name.bind("<KeyRelease>", lambda e: self.on_player_name_change(2))
        
        # Load saved name for player 2 (without updating buttons yet)
        robot_id = self.player2_id.get()
        if robot_id in self.player_names:
            self.player2_name.insert(0, self.player_names[robot_id])
        else:
            self.player2_name.insert(0, f"Player {robot_id}")
        
        # Battle buttons
        self.btn_start_battle = ttk.Button(battle_frame, text="Start Battle", command=self.start_battle,
                  width=20)
        self.btn_start_battle.grid(row=6, column=0, columnspan=2, pady=20)
        
        # Winner Frame
        winner_frame = ttk.LabelFrame(self.root, text="Declare Winner", padding=10)
        winner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_winner1 = ttk.Button(winner_frame, text="Player 1 Wins!", command=lambda: self.declare_winner(1),
                  width=25)
        self.btn_winner1.grid(row=0, column=0, padx=10, pady=5)
        
        self.btn_winner2 = ttk.Button(winner_frame, text="Player 2 Wins!", command=lambda: self.declare_winner(2),
                  width=25)
        self.btn_winner2.grid(row=0, column=1, padx=10, pady=5)
        
        # Update button text with initial names
        self.update_winner_buttons()
        
        # Status/Log Frame
        log_frame = ttk.LabelFrame(self.root, text="Status Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Disable controls initially (not connected)
        self.update_controls_state(False)
    
    def update_controls_state(self, connected: bool):
        """Enable or disable control buttons based on connection state."""
        # Connection controls (inverse logic - enabled when NOT connected)
        connection_state = tk.DISABLED if connected else tk.NORMAL
        self.btn_connect.config(state=connection_state)
        self.btn_refresh.config(state=connection_state)
        self.port_combo.config(state="disabled" if connected else "readonly")
        
        # Disconnect button (enabled when connected)
        self.btn_disconnect.config(state=tk.NORMAL if connected else tk.DISABLED)
        
        # Control buttons (enabled when connected)
        control_state = tk.NORMAL if connected else tk.DISABLED
        self.btn_mute.config(state=control_state)
        self.btn_unmute.config(state=control_state)
        self.btn_stop.config(state=control_state)
        self.btn_enable.config(state=control_state)
        self.btn_start_battle.config(state=control_state)
        self.btn_winner1.config(state=control_state)
        self.btn_winner2.config(state=control_state)
    
    def refresh_ports(self):
        """Refresh available serial ports."""
        ports = serial.tools.list_ports.comports()
        port_list = [f"{port.device} - {port.description}" for port in ports]
        self.port_combo['values'] = port_list
        if port_list:
            self.port_combo.current(0)
            self.log(f"Found {len(port_list)} port(s)")
        else:
            self.log("No serial ports found")
    
    def connect(self):
        """Connect to selected serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.log("Already connected")
            return
        
        if not self.port_combo.get():
            messagebox.showerror("Error", "Please select a port")
            return
        
        port_name = self.port_combo.get().split(" - ")[0]
        
        try:
            self.serial_port = serial.Serial(port_name, 9600, timeout=1)
            # Read the identification string
            response = self.serial_port.readline().decode().strip()
            if response == "commander":
                self.connection_status.config(text=f"Connected to {port_name}", foreground="green")
                self.log(f"Connected to {port_name} (verified)")
                self.update_controls_state(True)
            else:
                self.connection_status.config(text=f"Connected to {port_name} (unverified)", foreground="orange")
                self.log(f"Connected to {port_name} but didn't receive 'commander' greeting")
                self.update_controls_state(True)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.log(f"Connection failed: {e}")
            self.serial_port = None
    
    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port = None
            self.connection_status.config(text="Not Connected", foreground="red")
            self.update_controls_state(False)
            self.log("Disconnected")
        else:
            self.log("Not connected")
    
    def send_command(self, command: str) -> bool:
        """Send command to micro:bit and wait for response."""
        if not self.serial_port or not self.serial_port.is_open:
            messagebox.showerror("Error", "Not connected to serial port")
            return False
        
        try:
            self.serial_port.write(f"{command}\r".encode())
            
            # Read echo
            echo = self.serial_port.readline().decode().strip()
            # Read response
            response = self.serial_port.readline().decode().strip()
            
            if response == "OK":
                self.log(f"✓ {command}")
                return True
            else:
                self.log(f"✗ {command} - Response: {response}")
                return False
        except Exception as e:
            messagebox.showerror("Communication Error", f"Failed to send command: {e}")
            self.log(f"Error sending '{command}': {e}")
            return False
    
    def load_player_name(self, player: int):
        """Load saved player name for selected robot ID."""
        if player == 1:
            robot_id = self.player1_id.get()
            name_entry = self.player1_name
        else:
            robot_id = self.player2_id.get()
            name_entry = self.player2_name
        
        # Clear current name
        name_entry.delete(0, tk.END)
        
        # Load saved name if exists, otherwise use default
        if robot_id in self.player_names:
            name_entry.insert(0, self.player_names[robot_id])
        else:
            name_entry.insert(0, f"Player {robot_id}")
        
        # Update winner button text
        self.update_winner_buttons()
    
    def on_player_name_change(self, player: int):
        """Handle player name change event."""
        self.save_player_name(player)
        self.update_winner_buttons()
    
    def update_winner_buttons(self):
        """Update the text on winner buttons to show current player names."""
        name1 = self.player1_name.get() or "Player 1"
        name2 = self.player2_name.get() or "Player 2"
        self.btn_winner1.config(text=f"{name1} Wins!")
        self.btn_winner2.config(text=f"{name2} Wins!")
    
    def save_player_name(self, player: int):
        """Save player name to config."""
        if player == 1:
            robot_id = self.player1_id.get()
            name = self.player1_name.get()
        else:
            robot_id = self.player2_id.get()
            name = self.player2_name.get()
        
        if name.strip():
            self.player_names[robot_id] = name
            self.save_config()
    
    def start_battle(self):
        """Start a battle between two players."""
        try:
            p1_id = int(self.player1_id.get())
            p2_id = int(self.player2_id.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid robot IDs")
            return
        
        if p1_id == p2_id:
            messagebox.showerror("Error", "Players must have different robot IDs")
            return
        
        if not (0 <= p1_id <= 15 and 0 <= p2_id <= 15):
            messagebox.showerror("Error", "Robot IDs must be between 0 and 15")
            return
        
        # Save names
        self.save_player_name(1)
        self.save_player_name(2)
        
        p1_name = self.player1_name.get() or f"Player {p1_id}"
        p2_name = self.player2_name.get() or f"Player {p2_id}"
        
        if self.send_command(f"battle,{p1_id},{p2_id}"):
            self.log(f"⚔ Battle started: {p1_name} (ID {p1_id}) vs {p2_name} (ID {p2_id})")
    
    def declare_winner(self, player: int):
        """Declare the winner of the battle."""
        try:
            if player == 1:
                winner_id = int(self.player1_id.get())
                winner_name = self.player1_name.get() or f"Player {winner_id}"
            else:
                winner_id = int(self.player2_id.get())
                winner_name = self.player2_name.get() or f"Player {winner_id}"
        except ValueError:
            messagebox.showerror("Error", "Invalid robot ID")
            return
        
        if not (0 <= winner_id <= 15):
            messagebox.showerror("Error", "Robot ID must be between 0 and 15")
            return
        
        if self.send_command(f"winner,{winner_id}"):
            self.log(f"🏆 Winner: {winner_name} (ID {winner_id})")
    
    def log(self, message: str):
        """Add message to status log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = BattleBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
