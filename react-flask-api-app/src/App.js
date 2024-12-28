// import logo from "./logo.svg";
import "./App.css";
// import React, { useEffect, useState } from "react";
// import axios from 'axios';

// function App() {
//   const [accuracy, setAccuracy] = useState("");

// useEffect(() => {
//   // fetch(`/api/ml`).then(res => res.json()).then(data => {setAccuracy(data.accuracy)});
//   axios.post("/api/ml", {
//     string: "lol"
//   }).then(
//     (response) => {
//       setAccuracy(response.data.lol);
//     },
//     (error) => {
//       console.log(error);
//     }
//   );
// }, []);

//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>Output: {accuracy}</p>
//       </header>
//     </div>
//   );
// }

// export default App;

import React, { useState } from "react";
import neo4j from "neo4j-driver";
import axios from "axios";

const App = () => {
  const [query, setQuery] = useState("");
  const [forwardQuery, setForwardQuery] = useState("");
  const [result, setResult] = useState([]);

  const executeQuery = async () => {
    axios
      .post("/api/query", {
        string: query,
      })
      .then(
        (response) => {
          setForwardQuery(response.data.query);
          console.log("lol")
          console.log(forwardQuery);
        },
        (error) => {
          console.log(error);
        }
      );

    const driver = neo4j.driver(
      "bolt+s://99a16ad0.databases.neo4j.io",
      neo4j.auth.basic("neo4j", "Jw7GZzMhCOGEJa1NVDFXwlz2wFJ4CaCVMb-0wzq_b9A")
    );
    const session = driver.session();

    try {
      // const neo4jQuery = `MATCH (c:Case {Author: 'V Bose'}) RETURN c.Verdict AS result;`; // Replace with your actual query
      const neo4jQuery = forwardQuery;
      const neo4jResult = await session.run(neo4jQuery);

      const records = neo4jResult.records.map((record) => record.toObject());
      setResult(records);
    } catch (error) {
      console.error("Error executing Neo4j query:", error);
    } finally {
      await session.close();
      await driver.close();
    }
  };

  const tableRows = result.map((item, index) => (
    <tr key={index}>
      <td>{item.Case_Name}</td>
      <td>{item.Judgement_Date}</td>
      <td>{item.Author}</td>
      <td>{item.Bench}</td>
      <td>{item.CaseID_CitationID}</td>
      <td>{item.Verdict}</td>
      <td>{item.IPC}</td>
      <td>{item.CRPC}</td>
      <td>{item.CPC}</td>
      <td>{item.Acts}</td>
    </tr>
  ));

  return (
    <div className="App">
      <h2>LEGAL DOCUMENT QUERY SYSTEM</h2>
      <div>
        <div>
          <textarea value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
        <div>
          <button className="Execute-query-button" onClick={executeQuery}>
            Execute Query
          </button>
        </div>
      </div>

      <h3>Table from JSON Data</h3>
      <table className="result-table" border="1">
        <thead>
          <tr>
            <th>Case_Name</th>
            <th>Judgement_Date</th>
            <th>Author</th>
            <th>Bench</th>
            <th>CaseID_CitationID</th>
            <th>Verdict</th>
            <th>IPC</th>
            <th>CRPC</th>
            <th>CPC</th>
            <th>Acts</th>
          </tr>
        </thead>
        <tbody>{tableRows}</tbody>
      </table>
      <div>
        <h3>Query Result in JSON</h3>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </div>
      <footer>Aditi Agarwal, Atharv Patil, Krishna Shreeram</footer>
    </div>
  );
};

export default App;
