/**
 * PinkPapa — envio direto da proposta por e-mail (com PDF em anexo).
 * Mesmo padrão do Apps Script da Controladoria do Raio-X (MailApp, sem SMTP).
 *
 * COMO PUBLICAR (uma vez):
 *  1. script.google.com  ->  Novo projeto  ->  cole este arquivo.
 *  2. Implantar  ->  Nova implantação  ->  Tipo: "App da Web".
 *  3. Executar como: EU  |  Quem pode acessar: QUALQUER PESSOA.
 *  4. Copie a URL /exec e cole em ~/pinkpapa/mail_endpoint.txt
 *  5. Rode ~/pinkpapa/publicar.sh  (o painel passa a enviar de verdade).
 *
 * Ao alterar este arquivo, use "Gerenciar implantações" -> nova versão
 * (a URL /exec não muda).
 */

// cópia oculta fixa (opcional) — recebe todas as propostas enviadas
var BCC_FIXO = 'g3.healthservice@proton.me';

function doPost(e) {
  try {
    var p = JSON.parse(e.postData.contents);

    if (p.action === 'enviarProposta') {
      var anexo = Utilities.newBlob(
        Utilities.base64Decode(p.pdfBase64),
        'application/pdf',
        p.nomeArquivo || 'Proposta_PinkPapa.pdf'
      );

      var opts = {
        name: 'G3 Health Service — PinkPapa',
        attachments: [anexo],
        bcc: [BCC_FIXO, p.copia].filter(function (x) { return x; }).join(',')
      };
      if (p.copia) opts.replyTo = p.copia;

      MailApp.sendEmail(p.para, p.assunto, p.corpo, opts);
      _log(p);
      return _ok({ enviado: true, para: p.para });
    }

    return _ok({ erro: 'acao desconhecida' });
  } catch (err) {
    return _ok({ erro: String(err) });
  }
}

/** registra o envio numa aba "Propostas" (auditoria simples) */
function _log(p) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) return; // script standalone, sem planilha: ignora
    var sh = ss.getSheetByName('Propostas');
    if (!sh) {
      sh = ss.insertSheet('Propostas');
      sh.appendRow(['Data', 'Destinatario', 'Alvo', 'Referencia', 'Valor', 'Arquivo']);
    }
    sh.appendRow([new Date(), p.para, p.alvo, p.ref, p.valor, p.nomeArquivo]);
  } catch (e) { /* nao bloqueia o envio */ }
}

function _ok(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return _ok({ status: 'PinkPapa mailer ativo' });
}
