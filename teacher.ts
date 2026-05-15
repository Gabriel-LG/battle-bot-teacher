
/**
* Use this file to define custom functions and blocks.
* Read more at https://makecode.microbit.org/blocks/custom
*/


/**
 * Custom blocks
 */

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
        flags |= state.motorsEnabled ? 0x00 : 0x02;
        flags |= state.victory ? 0x80 : 0x00;

        let buffer: Buffer = pins.createBuffer(2);
        buffer.setUint8(0, 0x54 /*'T'*/); // 'T' for teacher update
        buffer.setNumber(NumberFormat.Int8BE, 1, flags);
        radio.sendBuffer(buffer);
    }
}