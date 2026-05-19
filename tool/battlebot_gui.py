#!/usr/bin/env python3
"""
BattleBot Teacher GUI
A graphical interface for controlling BattleBot robots via micro:bit serial interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import serial
import serial.tools.list_ports
import json
import os
import threading
import time
import re
from typing import Optional


class BattleBotGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BattleBot Teacher Control")
        self.root.geometry("600x600")
        self.serial_port: Optional[serial.Serial] = None
        self.connection_verified: bool = False
        self.command_in_progress: bool = False  # Track if long command is executing
        
        # Controller detection
        self.controller_detected = False
        self.read_thread: Optional[threading.Thread] = None
        self.stop_reading = False
        
        # Load player names from config (in same directory as script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(script_dir, "battlebot_config.json")
        config = self.load_config()
        self.player_names = config.get("player_names", {})
        self.robot_names = config.get("robot_names", {})
        
        self.create_widgets()
        self.refresh_ports()
        
    def load_config(self) -> dict:
        """Load player and robot names from config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {"player_names": {}, "robot_names": {}}
        return {"player_names": {}, "robot_names": {}}
    
    def save_config(self):
        """Save player and robot names to config file."""
        try:
            config = {
                "player_names": self.player_names,
                "robot_names": self.robot_names
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Serial Port Selection Frame
        port_frame = ttk.LabelFrame(self.root, text="Serial Connection", padding=10)
        port_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(port_frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.port_combo = ttk.Combobox(port_frame, width=30, state="readonly")
        self.port_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W)
        
        self.btn_refresh = ttk.Button(port_frame, text="Refresh", command=self.refresh_ports)
        self.btn_refresh.grid(row=0, column=3, padx=5)
        
        self.btn_connect = ttk.Button(port_frame, text="Connect", command=self.connect, width=15)
        self.btn_connect.grid(row=1, column=1, padx=(0, 5), pady=(5, 0), sticky=tk.W)
        
        self.btn_disconnect = ttk.Button(port_frame, text="Disconnect", command=self.disconnect, width=15)
        self.btn_disconnect.grid(row=1, column=2, pady=(5, 0), sticky=tk.W)
        
        self.connection_status = ttk.Label(port_frame, text="Not Connected", foreground="red")
        self.connection_status.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Global Controls Frame
        global_frame = ttk.LabelFrame(self.root, text="Global Controls", padding=10)
        global_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_mute = ttk.Button(global_frame, text="Mute All", command=lambda: self.send_command("mute,1"), 
                  width=20)
        self.btn_mute.grid(row=0, column=0, padx=5, pady=5)
        
        self.btn_halt = ttk.Button(global_frame, text="Halt All Motors", command=lambda: self.send_command("halt,1"),
                  width=20)
        self.btn_halt.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_freeze = ttk.Button(global_frame, text="Freeze All Servos", command=lambda: self.send_command("freeze,1"),
                  width=20)
        self.btn_freeze.grid(row=0, column=2, padx=5, pady=5)
        
        self.btn_unmute = ttk.Button(global_frame, text="Unmute All", command=lambda: self.send_command("mute,0"),
                  width=20)
        self.btn_unmute.grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_unhalt = ttk.Button(global_frame, text="Unhalt All Motors", command=lambda: self.send_command("halt,0"),
                  width=20)
        self.btn_unhalt.grid(row=1, column=1, padx=5, pady=5)
        
        self.btn_unfreeze = ttk.Button(global_frame, text="Unfreeze All Servos", command=lambda: self.send_command("freeze,0"),
                  width=20)
        self.btn_unfreeze.grid(row=1, column=2, padx=5, pady=5)
        
        # Battle Controls Frame
        battle_frame = ttk.LabelFrame(self.root, text="Battle Setup", padding=10)
        battle_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Configure columns for consistent width
        battle_frame.columnconfigure(0, weight=1, uniform="player")
        battle_frame.columnconfigure(1, weight=0)
        battle_frame.columnconfigure(2, weight=1, uniform="player")
        
        # Column headers - centered above fields
        ttk.Label(battle_frame, text="Controller:", font=("Arial", 9)).grid(row=0, column=0, padx=10, pady=(5, 2))
        ttk.Label(battle_frame, text="Controller:", font=("Arial", 9)).grid(row=0, column=2, padx=10, pady=(5, 2))
        
        # Robot ID spinboxes
        self.player1_id = ttk.Spinbox(battle_frame, from_=0, to=41, width=10, command=lambda: self.load_player_name(1))
        self.player1_id.set(0)
        self.player1_id.grid(row=1, column=0, padx=10, pady=2)
        self.player1_id.bind("<KeyRelease>", lambda e: self.load_player_name(1))
        self.player1_id.bind("<FocusOut>", lambda e: self.validate_and_fix_id(1))
        self.player1_id.bind("<Return>", lambda e: self.focus_next(self.player1_name))
        self.player1_id.bind("<Tab>", lambda e: self.focus_next(self.player1_name))
        
        # Versus label (centered vertically across rows 1-5)
        ttk.Label(battle_frame, text="Versus", font=("Arial", 14, "bold")).grid(row=1, column=1, rowspan=5, padx=30)
        
        self.player2_id = ttk.Spinbox(battle_frame, from_=0, to=41, width=10, command=lambda: self.load_player_name(2))
        self.player2_id.set(1)
        self.player2_id.grid(row=1, column=2, padx=10, pady=2)
        self.player2_id.bind("<KeyRelease>", lambda e: self.load_player_name(2))
        self.player2_id.bind("<FocusOut>", lambda e: self.validate_and_fix_id(2))
        self.player2_id.bind("<Return>", lambda e: self.focus_next(self.player2_name))
        self.player2_id.bind("<Tab>", lambda e: self.focus_next(self.player2_name))
        
        # Player name labels
        ttk.Label(battle_frame, text="Player:", font=("Arial", 9)).grid(row=2, column=0, padx=10, pady=(10, 2))
        ttk.Label(battle_frame, text="Player:", font=("Arial", 9)).grid(row=2, column=2, padx=10, pady=(10, 2))
        
        # Player name entry fields
        self.player1_name = ttk.Entry(battle_frame, width=20)
        self.player1_name.grid(row=3, column=0, padx=10, pady=2)
        self.player1_name.bind("<FocusOut>", lambda e: self.on_player_name_change(1))
        self.player1_name.bind("<KeyRelease>", lambda e: self.on_player_name_change(1))
        self.player1_name.bind("<Return>", lambda e: self.focus_next(self.player1_robot))
        self.player1_name.bind("<Tab>", lambda e: self.focus_next(self.player1_robot))
        
        self.player2_name = ttk.Entry(battle_frame, width=20)
        self.player2_name.grid(row=3, column=2, padx=10, pady=2)
        self.player2_name.bind("<FocusOut>", lambda e: self.on_player_name_change(2))
        self.player2_name.bind("<KeyRelease>", lambda e: self.on_player_name_change(2))
        self.player2_name.bind("<Return>", lambda e: self.focus_next(self.player2_robot))
        self.player2_name.bind("<Tab>", lambda e: self.focus_next(self.player2_robot))
        
        # Robot name labels
        ttk.Label(battle_frame, text="Robot:", font=("Arial", 9)).grid(row=4, column=0, padx=10, pady=(10, 2))
        ttk.Label(battle_frame, text="Robot:", font=("Arial", 9)).grid(row=4, column=2, padx=10, pady=(10, 2))
        
        # Robot name entry fields
        self.player1_robot = ttk.Entry(battle_frame, width=20)
        self.player1_robot.grid(row=5, column=0, padx=10, pady=2)
        self.player1_robot.bind("<FocusOut>", lambda e: self.on_robot_name_change(1))
        self.player1_robot.bind("<KeyRelease>", lambda e: self.on_robot_name_change(1))
        self.player1_robot.bind("<Return>", lambda e: self.focus_next(self.player2_id))
        self.player1_robot.bind("<Tab>", lambda e: self.focus_next(self.player2_id))
        
        self.player2_robot = ttk.Entry(battle_frame, width=20)
        self.player2_robot.grid(row=5, column=2, padx=10, pady=2)
        self.player2_robot.bind("<FocusOut>", lambda e: self.on_robot_name_change(2))
        self.player2_robot.bind("<KeyRelease>", lambda e: self.on_robot_name_change(2))
        self.player2_robot.bind("<Return>", lambda e: self.focus_next(self.btn_start_battle))
        self.player2_robot.bind("<Tab>", lambda e: self.focus_next(self.btn_start_battle))
        
        # Load saved names for both players
        self.load_player_name(1)
        self.load_player_name(2)
        
        # Battle button
        self.btn_start_battle = ttk.Button(battle_frame, text="Fight!", command=self.start_battle,
                  width=30)
        self.btn_start_battle.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Winner Frame (with border, aligned with battle frame)
        winner_frame = ttk.LabelFrame(self.root, text="Declare Winner", padding=10)
        winner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Configure columns to match battle frame exactly
        winner_frame.columnconfigure(0, weight=1, uniform="player")
        winner_frame.columnconfigure(1, weight=0)
        winner_frame.columnconfigure(2, weight=1, uniform="player")
        
        self.btn_winner1 = ttk.Button(winner_frame, text="Player 1 Wins!", command=lambda: self.declare_winner(1),
                  width=20)
        self.btn_winner1.grid(row=0, column=0, padx=10, pady=5)
        
        # Empty spacer label to maintain center column
        ttk.Label(winner_frame, text="").grid(row=0, column=1)
        
        self.btn_winner2 = ttk.Button(winner_frame, text="Player 2 Wins!", command=lambda: self.declare_winner(2),
                  width=20)
        self.btn_winner2.grid(row=0, column=2, padx=10, pady=5)
        
        # Update button text with initial names
        self.update_winner_buttons()
        
        # Spacer frame that expands to take remaining vertical space (when log is hidden)
        self.spacer_frame = ttk.Frame(self.root)
        self.spacer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status/Log toggle button frame (at bottom when hidden)
        self.log_header_frame = ttk.Frame(self.root)
        self.log_header_frame.pack(fill=tk.X, padx=10, pady=(5, 5))
        
        self.log_visible = tk.BooleanVar(value=False)
        self.btn_toggle_log = ttk.Button(self.log_header_frame, text="▶ Show Status Log", command=self.toggle_log)
        self.btn_toggle_log.pack(side=tk.LEFT)
        
        self.log_frame = ttk.LabelFrame(self.root, text="Status Log", padding=5)
        # Don't pack initially (collapsed by default)
        
        self.log_text = tk.Text(self.log_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Disable controls initially (not connected)
        self.update_controls_state(False)
    
    def validate_and_fix_id(self, player: int):
        """Validate and correct robot ID when focus leaves the field."""
        spinbox = self.player1_id if player == 1 else self.player2_id
        try:
            value = int(spinbox.get())
            # Clamp to valid range (0-41)
            if value < 0:
                spinbox.set(0)
            elif value > 41:
                spinbox.set(41)
        except ValueError:
            # Not a valid number, reset to 0
            spinbox.set(0)
        
        # Update player name after correction
        self.load_player_name(player)
    
    def toggle_log(self):
        """Toggle visibility of status log."""
        if self.log_visible.get():
            # Hide log - restore spacer and move toggle button back to bottom
            self.log_frame.pack_forget()
            
            # Restore spacer frame to fill space
            self.spacer_frame.pack(fill=tk.BOTH, expand=True)
            
            # Move log header back to bottom (after spacer)
            self.log_header_frame.pack_forget()
            self.log_header_frame.pack(fill=tk.X, padx=10, pady=(5, 5))
            
            self.btn_toggle_log.config(text="▶ Show Status Log")
            self.log_visible.set(False)
        else:
            # Show log - move toggle button right after winner frame and hide spacer
            # Reposition toggle button header before spacer (while it's still packed)
            self.log_header_frame.pack_forget()
            self.log_header_frame.pack(fill=tk.X, padx=10, pady=(5, 0), before=self.spacer_frame)
            
            # Now hide spacer and show log frame to fill remaining space
            self.spacer_frame.pack_forget()
            self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            self.btn_toggle_log.config(text="▼ Hide Status Log")
            self.log_visible.set(True)
    
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
        self.btn_halt.config(state=control_state)
        self.btn_unhalt.config(state=control_state)
        self.btn_freeze.config(state=control_state)
        self.btn_unfreeze.config(state=control_state)
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
            self.btn_connect.config(state=tk.NORMAL)
            self.log(f"Found {len(port_list)} port(s)")
        else:
            self.port_combo.set('')  # Clear the selection when no ports available
            self.btn_connect.config(state=tk.DISABLED)
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
            self.connection_status.config(text=f"Connected to {port_name}", foreground="orange")
            self.log(f"Connected to {port_name} (not yet verified)")
            self.connection_verified = False
            self.controller_detected = False
            self.update_controls_state(True)
            
            # Start background thread to monitor for controller messages
            self.stop_reading = False
            self.read_thread = threading.Thread(target=self.monitor_serial, daemon=True)
            self.read_thread.start()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.log(f"Connection failed: {e}")
            self.serial_port = None
    
    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.stop_reading = True
            if self.read_thread:
                self.read_thread.join(timeout=2)
            
            self.serial_port.close()
            self.serial_port = None
            self.connection_verified = False
            self.controller_detected = False
            self.connection_status.config(text="Not Connected", foreground="red")
            self.update_controls_state(False)
            self.log("Disconnected")
        else:
            self.log("Not connected")
    
    def send_command(self, command: str, threaded: bool = False) -> bool:
        """Send command to micro:bit and wait for response.
        
        Args:
            command: The command to send
            threaded: If True, run in background thread (for long commands)
        """
        if threaded:
            # Run in background thread to keep GUI responsive
            thread = threading.Thread(target=self._send_command_impl, args=(command,), daemon=True)
            thread.start()
            return True
        else:
            return self._send_command_impl(command)
    
    def _send_command_impl(self, command: str) -> bool:
        """Internal implementation of send_command."""
        if not self.serial_port or not self.serial_port.is_open:
            self.root.after(0, lambda: messagebox.showerror("Error", "Not connected to serial port"))
            return False
        
        # Check if a long command is already in progress
        if self.command_in_progress:
            self.root.after(0, lambda: self.log("⏳ Command already in progress, please wait..."))
            return False
        
        try:
            # Increase timeout for battle/winner commands as they take longer
            old_timeout = self.serial_port.timeout
            is_long_command = command.startswith("battle,") or command.startswith("winner,")
            
            if command.startswith("battle,"):
                self.serial_port.timeout = 10  # 10 seconds for battle (animations + music ~8s)
            elif command.startswith("winner,"):
                self.serial_port.timeout = 6  # 6 seconds for winner (animations ~5s)
            
            # Disable buttons for long commands
            if is_long_command:
                self.command_in_progress = True
                self.root.after(0, lambda: self.update_controls_state(False))  # Disable all controls
            
            self.serial_port.write(f"{command}\r".encode())
            
            # Read echo
            echo = self.serial_port.readline().decode().strip()
            # Read response
            response = self.serial_port.readline().decode().strip()
            
            # Restore original timeout
            self.serial_port.timeout = old_timeout
            
            # Re-enable buttons for long commands
            if is_long_command:
                self.command_in_progress = False
                self.root.after(0, lambda: self.update_controls_state(True))  # Re-enable all controls
            
            if response == "OK":
                # Mark connection as verified on first successful command
                if not self.connection_verified:
                    self.connection_verified = True
                    port_name = self.port_combo.get().split(" - ")[0]
                    self.root.after(0, lambda: self.connection_status.config(text=f"Connected to {port_name} (verified)", foreground="green"))
                
                self.root.after(0, lambda: self.log(f"✓ {command} - Response: {response}"))
                return True
            else:
                self.root.after(0, lambda: self.log(f"✗ {command} - Response: {response}"))
                return False
        except Exception as e:
            # Restore timeout and re-enable buttons on error
            if 'old_timeout' in locals():
                self.serial_port.timeout = old_timeout
            if is_long_command:
                self.command_in_progress = False
                self.root.after(0, lambda: self.update_controls_state(True))
            self.root.after(0, lambda: messagebox.showerror("Communication Error", f"Failed to send command: {e}"))
            self.root.after(0, lambda: self.log(f"Error sending '{command}': {e}"))
            return False
    
    def monitor_serial(self):
        """Background thread to monitor serial input for controller messages."""
        import re
        controller_pattern = re.compile(r'Set ID \((\d+|NaN)\):', re.IGNORECASE)
        
        while not self.stop_reading and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:
                        match = controller_pattern.match(line)
                        if match:
                            current_id_str = match.group(1)
                            # Handle NaN (case insensitive) as None, otherwise convert to int
                            current_id = None if current_id_str.upper() == "NAN" else int(current_id_str)
                            if not self.controller_detected:
                                self.controller_detected = True
                                # Use after() to schedule GUI update on main thread
                                self.root.after(0, lambda: self.handle_controller_detected(current_id))
                
                time.sleep(0.1)
            except Exception as e:
                if not self.stop_reading:
                    self.root.after(0, lambda: self.log(f"Monitor error: {e}"))
                break
    
    def handle_controller_detected(self, current_id: Optional[int]):
        """Handle controller detection on main thread."""
        port_name = self.port_combo.get().split(" - ")[0]
        self.connection_status.config(text=f"Controller detected on {port_name}", foreground="blue")
        
        if current_id is None:
            self.log(f"🎮 Controller detected with ID: NAN (not set)")
            id_text = "NAN (not set)"
        else:
            self.log(f"🎮 Controller detected with ID {current_id}")
            id_text = str(current_id)
        
        # Ask user for new ID
        new_id = tk.simpledialog.askinteger(
            "Controller Detected",
            f"A BattleBot controller is connected.\n\nCurrent ID: {id_text}\n\nEnter new ID (0-15):",
            minvalue=0,
            maxvalue=15,
            initialvalue=current_id if current_id is not None else 0
        )
        
        if new_id is not None and new_id != current_id:
            self.set_controller_id(new_id)
            # Small delay to ensure command is sent before disconnect
            self.root.after(500, self.disconnect)
        else:
            # User cancelled or kept same ID
            self.disconnect()
    
    def set_controller_id(self, new_id: int):
        """Send new ID to controller."""
        try:
            self.serial_port.write(f"{new_id}\r".encode())
            self.log(f"✓ Controller ID set to {new_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set controller ID: {e}")
            self.log(f"✗ Failed to set controller ID: {e}")
    
    def focus_next(self, widget):
        """Move focus to the next widget."""
        widget.focus_set()
        return "break"  # Prevent default Tab/Enter behavior
    
    def load_player_name(self, player: int):
        """Load saved player and robot names for selected controller ID."""
        if player == 1:
            controller_id = self.player1_id.get()
            player_entry = self.player1_name
            robot_entry = self.player1_robot
        else:
            controller_id = self.player2_id.get()
            player_entry = self.player2_name
            robot_entry = self.player2_robot
        
        # Clear current names
        player_entry.delete(0, tk.END)
        robot_entry.delete(0, tk.END)
        
        # Load saved names if exist, otherwise use defaults
        if controller_id in self.player_names:
            player_entry.insert(0, self.player_names[controller_id])
        else:
            player_entry.insert(0, f"Player {controller_id}")
        
        if controller_id in self.robot_names:
            robot_entry.insert(0, self.robot_names[controller_id])
        else:
            robot_entry.insert(0, f"Robot {controller_id}")
        
        # Update winner button text
        self.update_winner_buttons()
    
    def on_player_name_change(self, player: int):
        """Handle player name change event."""
        self.save_player_name(player)
        self.update_winner_buttons()
    
    def on_robot_name_change(self, player: int):
        """Handle robot name change event."""
        self.save_robot_name(player)
        self.update_winner_buttons()
    
    def update_winner_buttons(self):
        """Update the text on winner buttons to show current player names."""
        # Only update if buttons have been created (they're created after initial load)
        if not hasattr(self, 'btn_winner1'):
            return
        
        name1 = self.player1_name.get() or "Player 1"
        name2 = self.player2_name.get() or "Player 2"
        self.btn_winner1.config(text=f"{name1} Wins!")
        self.btn_winner2.config(text=f"{name2} Wins!")
    
    def save_player_name(self, player: int):
        """Save player name to config."""
        if player == 1:
            controller_id = self.player1_id.get()
            name = self.player1_name.get()
        else:
            controller_id = self.player2_id.get()
            name = self.player2_name.get()
        
        if name.strip():
            self.player_names[controller_id] = name
            self.save_config()
    
    def save_robot_name(self, player: int):
        """Save robot name to config."""
        if player == 1:
            controller_id = self.player1_id.get()
            name = self.player1_robot.get()
        else:
            controller_id = self.player2_id.get()
            name = self.player2_robot.get()
        
        if name.strip():
            self.robot_names[controller_id] = name
            self.save_config()
    
    def start_battle(self):
        """Start a battle between two players."""
        # Check if command is already in progress before validation
        if self.command_in_progress:
            self.log("⏳ Command already in progress, please wait...")
            return
        
        try:
            p1_id = int(self.player1_id.get())
            p2_id = int(self.player2_id.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid robot IDs")
            return
        
        if p1_id == p2_id:
            messagebox.showerror("Error", "Players must have different robot IDs")
            return
        
        if not (0 <= p1_id <= 41 and 0 <= p2_id <= 41):
            messagebox.showerror("Error", "Robot IDs must be between 0 and 41")
            return
        
        # Save names
        self.save_player_name(1)
        self.save_player_name(2)
        
        p1_name = self.player1_name.get() or f"Player {p1_id}"
        p2_name = self.player2_name.get() or f"Player {p2_id}"
        
        self.log(f"⚔ Battle starting: {p1_name} (ID {p1_id}) vs {p2_name} (ID {p2_id})")
        self.send_command(f"battle,{p1_id},{p2_id}", threaded=True)
    
    def declare_winner(self, player: int):
        """Declare the winner of the battle."""
        # Check if command is already in progress before validation
        if self.command_in_progress:
            self.log("⏳ Command already in progress, please wait...")
            return
        
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
        
        if not (0 <= winner_id <= 41):
            messagebox.showerror("Error", "Robot ID must be between 0 and 41")
            return
        
        self.log(f"🏆 Declaring winner: {winner_name} (ID {winner_id})")
        self.send_command(f"winner,{winner_id}", threaded=True)
    
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
