// import { useState } from 'react'


function App() {
  // const [count, setCount] = useState(0)

  return (
    <>
      <div className="flex flex-wrap gap-2">
        <button className="btn btn-primary m-2 flex-1">Primary</button>
        <button className="btn btn-secondary m-2 flex-1">Secondary</button>
        <button className="btn btn-tertiary m-2 flex-1">Tertiary</button>
        <button className="btn btn-disable m-2 flex-1">Muted</button>
        <button className="btn btn-success m-2 flex-1">Success</button>
        <button className="btn btn-danger m-2 flex-1">Danger</button>
        <button className="btn m-2 flex-1">Save</button>
      </div>
    </>
  )
}

export default App
