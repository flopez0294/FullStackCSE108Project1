import React, {useEffect, useState} from 'react'
import './App.css';

function App() {
  const [yo,setData] = useState({});

  useEffect( () => {
    fetch('/member')
      .then((res) => {
        return res.json();
      })
      .then((data) => {
        console.log(data);
        setData(data);
      });
  }, [])

  return (
    <div className="App">
     
    </div>
  );
}

export default App;
