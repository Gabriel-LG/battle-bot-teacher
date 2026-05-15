
/**
* Use this file to define custom functions and blocks.
* Read more at https://makecode.microbit.org/blocks/custom
*/


/**
 * Custom blocks
 */
//% weight=100 color=#EE7202 icon="\uf11b"
//% block="BattleBot Controller"
namespace controller {
    let started: boolean = false;


    function sendUpdate(): void {
        let buttons: number = 0;
        let buffer: Buffer = pins.createBuffer(4);
        buttons |= input.buttonIsPressed(Button.A) ? 0x01 : 0x00;
        buttons |= input.buttonIsPressed(Button.B) ? 0x02 : 0x00;
        buttons |= joystickbit.getButton(joystickbit.JoystickBitPin.P12) ? 0x04 : 0x00;
        buttons |= joystickbit.getButton(joystickbit.JoystickBitPin.P13) ? 0x08 : 0x00;
        buttons |= joystickbit.getButton(joystickbit.JoystickBitPin.P14) ? 0x10 : 0x00;
        buttons |= joystickbit.getButton(joystickbit.JoystickBitPin.P15) ? 0x20 : 0x00;
        buttons |= input.logoIsPressed() ? 0x40 : 0x00;
        buttons |= input.isGesture(Gesture.Shake) ? 0x80 : 0x00;
        buffer.setUint8(0, 0x43 /*'C'*/); // 'C' for controller update
        buffer.setNumber(NumberFormat.Int8BE, 1, pins.map(joystickbit.getRockerValue(joystickbit.rockerType.X), 0, 1023, -127, 127));
        buffer.setNumber(NumberFormat.Int8BE, 2, pins.map(joystickbit.getRockerValue(joystickbit.rockerType.Y), 0, 1023, -127, 127));
        buffer.setNumber(NumberFormat.Int8BE, 3, buttons);
        radio.sendBuffer(buffer);
    }

    //% block
    export function initController(id: number): void {
        joystickbit.initJoystickBit();
        if (!started) control.setInterval(sendUpdate, 20, control.IntervalMode.Interval)
        radio.setGroup(0);
        radio.setFrequencyBand(id * 5);
        started = true;
    }
}

//% weight=100 color=#EE7202 icon="\uf0a1"
//% block="BattleBot Teacher"
namespace teacher {

    class State
    {
        constructor(){}
        soundEnabled: boolean = true;
        motorsEnabled: boolean = true;
        victory: boolean = false;
    }


    let state: {[id: number]: State} = {};

    function getState(id: number) : State
    {
        if (state[id] == undefined) state[id] = new State;
        return state[id];
    }



    //% block
    export function enableSound(id: number, enable: boolean): void {
        getState(id).soundEnabled = enable;
    }

    //% block
    export function enableMotors(id: number, enable: boolean): void {
        getState(id).motorsEnabled = enable;
    }

    //% block
    export function setVictory(id: number, value: boolean): void {
        getState(id).victory = value;
    }

    //% block
    export function transmitState(id: number): void {
        radio.setGroup(0);
        radio.setFrequencyBand(id * 5);

        let state: State = getState(id);

        let flags: number = 0;
        flags |= state.soundEnabled ? 0x00 : 0x01;
        flags |= state.motorsEnabled ? 0x00 : 0x01;
        flags |= state.victory ? 0x80 : 0x00;

        let buffer: Buffer = pins.createBuffer(2);
        buffer.setUint8(0, 0x54 /*'T'*/); // 'T' for teacher update
        buffer.setNumber(NumberFormat.Int8BE, 1, flags);
        radio.sendBuffer(buffer);
    }
}