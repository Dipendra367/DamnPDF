const cards = [
  {
    title: 'We never know who you are',
    body: 'No account, no email, no name, no tracking, no analytics. Nothing you do here can be connected back to you.',
  },
  {
    title: 'Your files are deleted automatically',
    body: 'Every uploaded file is deleted within 1 hour by an automated process — usually much sooner, the moment your conversion finishes. No backups, no database, nothing kept.',
  },
  {
    title: 'Random names only',
    body: 'While your file is being processed, it is stored under a random ID — never its original name. Even we could not tell whose file is whose.',
  },
  {
    title: 'The code is open',
    body: 'DamnPDF is open source. The deletion logic is a few lines you can read yourself — you do not have to take our word for it.',
  },
]

export default function Privacy() {
  return (
    <main className="page">
      <section className="privacy-hero">
        <h1>
          Privacy by design, <span>not by promise</span>
        </h1>
        <p>
          Most PDF tools ask you to trust them. DamnPDF shows you the receipts:
          anonymous by default, deleted within an hour, and open for anyone to
          verify.
        </p>
      </section>

      <section className="privacy-grid">
        {cards.map((c) => (
          <article key={c.title} className="privacy-card">
            <h2>{c.title}</h2>
            <p>{c.body}</p>
          </article>
        ))}
      </section>

      <section className="privacy-details">
        <h2>The honest details</h2>
        <ul>
          <li>
            <strong>What happens when you upload.</strong> Your file is sent
            over an encrypted connection (HTTPS) to our server, converted, and
            the result is sent back to you. The input file is deleted as soon
            as the conversion finishes; the output is deleted within 1 hour at
            the latest.
          </li>
          <li>
            <strong>Can the server see my file?</strong> Yes — for a few
            seconds, in order to convert it. This is true of every online PDF
            tool, including the big ones. What matters is that ours is deleted
            automatically and nobody ever looks at it.
          </li>
          <li>
            <strong>Do you keep logs?</strong> Our server keeps only the
            technical logs needed to run the service (timestamps, request
            sizes). Your filenames and file contents are never logged.
          </li>
          <li>
            <strong>Still don't trust us?</strong> Run DamnPDF yourself. It is
            self-hostable — clone the repository and the only person who can
            see your files is you.
          </li>
        </ul>
      </section>
    </main>
  )
}
