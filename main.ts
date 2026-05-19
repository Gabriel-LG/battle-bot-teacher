function muteAll (mute: number) {
    for (let index = 0; index <= 41; index++) {
        teacher.enableSound(index, mute == 0)
        teacher.transmitState(index)
    }
}
function winner (player: number) {
    for (let index = 0; index <= 41; index++) {
        if (0 != player) {
            teacher.enableSound(index, false)
            teacher.enableDriving(index, false)
            teacher.enableServos(index, false)
            teacher.transmitState(index)
        }
    }
    music.play(music.stringPlayable("C C - C C5 C5 C5 - ", 240), music.PlaybackMode.UntilDone)
    teacher.setVictory(player, true)
    teacher.enableSound(player, true)
    teacher.enableDriving(player, true)
    teacher.enableServos(player, true)
    teacher.transmitState(player)
    basic.pause(1000)
    teacher.setVictory(player, false)
    teacher.transmitState(player)
}
function freezeAll (freeze: number) {
    for (let index = 0; index <= 41; index++) {
        teacher.enableServos(index, freeze == 0)
        teacher.transmitState(index)
    }
}
function startBattle (player1: number, player2: number) {
    for (let index = 0; index <= 41; index++) {
        teacher.enableSound(index, false)
        teacher.enableDriving(index, false)
        teacher.enableServos(index, false)
        teacher.transmitState(index)
    }
    teacher.enableSound(player1, true)
    teacher.enableSound(player2, true)
    teacher.enableServos(player1, true)
    teacher.enableServos(player2, true)
    teacher.transmitState(player1)
    teacher.transmitState(player2)
    music.play(music.stringPlayable("C - C - C - C5 C5 ", 90), music.PlaybackMode.UntilDone)
    teacher.enableDriving(player1, true)
    teacher.enableDriving(player2, true)
    teacher.transmitState(player1)
    teacher.transmitState(player2)
}
function haltAll (halt: number) {
    for (let index = 0; index <= 41; index++) {
        teacher.enableDriving(index, halt == 0)
        teacher.transmitState(index)
    }
}
serial.onDataReceived(serial.delimiters(Delimiters.CarriageReturn), function () {
    line = serial.readUntil(serial.delimiters(Delimiters.CarriageReturn))
    serial.writeLine(line)
    command = line.split(",")[0]
    arg1 = parseFloat(line.split(",")[1])
    arg2 = parseFloat(line.split(",")[2])
    if (command == "mute") {
        muteAll(arg1)
        serial.writeLine("OK")
    } else if (command == "halt") {
        haltAll(arg1)
        serial.writeLine("OK")
    } else if (command == "freeze") {
        haltAll(arg1)
        serial.writeLine("OK")
    } else if (command == "battle") {
        startBattle(arg1, arg2)
        serial.writeLine("OK")
    } else if (command == "winner") {
        winner(arg1)
        serial.writeLine("OK")
    } else {
        serial.writeLine("ERROR")
    }
})
let arg2 = 0
let arg1 = 0
let command = ""
let line = ""
serial.redirectToUSB()
serial.setBaudRate(BaudRate.BaudRate9600)
serial.writeLine("commander")
// Iterating all IDs takes ~41 ms
loops.everyInterval(100, function () {
    for (let index2 = 0; index2 <= 41; index2++) {
        teacher.transmitState(index2)
    }
})
