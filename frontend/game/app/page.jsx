"use client";
import Image from "next/image";
import {useEffect,useState,useRef } from "react";
import "./test.css";
// let a= 0;



export default function Home() {

  const [message , setmessage] = useState("waiting for players to join!")
  const [table, settable] = useState([' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '])
  const socketRef = useRef(null);
  const [strikename, setstrikename] = useState("")
  const [logo, setlogo] = useState("java")
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/firstconsumer/`);
    socketRef.current = ws;
    ws.onopen = () => console.log("WebSocket connection established!");
    ws.onmessage = (event) => {
    // let data = JSON.stringify(event.data)
    let data = JSON.parse(event.data)

    let tmp_message = ""
    console.log(data)
    let table = data.table
    console.log(table)
    console.log(data)
    settable(table)
    let turn = data.turn
    if (data?.endgame)
      {
        tmp_message = `Game Over!`
        if (data?.class)
          {
          tmp_message += ` winner is ${data.winner}`
          setstrikename(data.class)
        }
        else
        tmp_message += ` It's a draw!`
    }
    else
    {
      if (data?.logo)
          setlogo(data.logo);
    if (turn)
    {
      // setturn(true)
      tmp_message = `Your turn!`

    }
    else
    {
      // setturn(false)
      tmp_message = `Opponent's turn!`
    }
    }
    setmessage(tmp_message);
    // ws.send(data);
    }
},[]);
  // let message = "hello world"
  // useEffect(()=>{
  //   console.log("render");
  // })
  return (
      <>
      <p>{message}</p>
      <div className = "board">
      {Array(9).fill(0).map((current, index) => (
        <div onClick = { () => socketRef.current.send(JSON.stringify({"index" : index}))} key={index}
        className={`tile ${(logo == "java" || table[index] != ' ')? "" : (logo == 'X'  ? "x-hover" : "o-hover")}`} >
          {table[index]}
        </div>
      ))}
      <div className={strikename}></div>
      </div>
      <br/>
      <button className = "hd" onClick = { () => {
        socketRef.current.send(JSON.stringify({"join_again" : true}))}}>Play again!</button>
    </>
  );
}
