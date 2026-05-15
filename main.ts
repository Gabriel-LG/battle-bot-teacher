function muteAll (mute: number) {
    for (let index = 0; index <= 15; index++) {
        teacher.enableSound(index, mute == 0)
        teacher.transmitState(index)
    }
}
function winner (player: number) {
    for (let index = 0; index <= 15; index++) {
        if (index != player) {
            teacher.enableSound(index, false)
            teacher.enableMotors(index, false)
            teacher.transmitState(index)
        }
    }
    music.play(music.stringPlayable("C C - C C5 C5 C5 - ", 240), music.PlaybackMode.UntilDone)
    teacher.setVictory(player, true)
    teacher.enableSound(player, true)
    teacher.enableMotors(player, true)
    teacher.transmitState(player)
    basic.pause(1000)
    teacher.setVictory(player, false)
    teacher.transmitState(player)
}
function stopAll (mute: number) {
    for (let index = 0; index <= 15; index++) {
        teacher.enableMotors(index, mute == 0)
        teacher.transmitState(index)
    }
}
function startBattle (player1: number, player2: number) {
    for (let index = 0; index <= 15; index++) {
        teacher.enableSound(index, false)
        teacher.enableMotors(index, false)
        teacher.transmitState(index)
    }
    teacher.enableSound(player1, true)
    teacher.enableSound(player2, true)
    teacher.transmitState(player1)
    teacher.transmitState(player2)
    music.play(music.stringPlayable("C - C - C - C5 C5 ", 90), music.PlaybackMode.UntilDone)
    teacher.enableMotors(player1, true)
    teacher.enableMotors(player2, true)
    teacher.transmitState(player1)
    teacher.transmitState(player2)
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
    } else if (command == "stop") {
        stopAll(arg1)
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
