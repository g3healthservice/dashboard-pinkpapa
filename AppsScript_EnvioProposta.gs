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
 * AO ATUALIZAR este arquivo: "Gerenciar implantações" -> editar (lápis)
 * -> Versão: "Nova versão" -> Implantar. A URL /exec NÃO muda.
 *
 * SEGURANÇA (2 camadas):
 *  - TOKEN: precisa bater com o token do painel. Barra quem tem só a URL
 *    (ex.: vazou num log) mas não a página. Não é segredo forte (o painel é
 *    estático e público), então é só a 1a camada.
 *  - RATE LIMIT server-side (MAX_POR_HORA): proteção REAL contra abuso —
 *    limita o total de envios por hora, independentemente de quem chame.
 */

var TOKEN        = 'ppapa-8f3a1c92';        // deve ser IGUAL ao ~/pinkpapa/mail_token.txt
var MAX_POR_HORA = 40;                       // teto de envios por hora (anti-abuso)
var BCC_FIXO     = 'g3.healthservice@proton.me';  // cópia oculta de auditoria

function doPost(e) {
  try {
    var p = JSON.parse(e.postData.contents);

    if (p.action === 'enviarProposta') {
      // 1a camada: token
      if (String(p.token) !== TOKEN) return _ok({ erro: 'token invalido' });

      // 2a camada: rate limit por hora (bucket no CacheService)
      var cache = CacheService.getScriptCache();
      var bucket = 'cnt_' + Math.floor(Date.now() / 3600000);
      var cnt = Number(cache.get(bucket) || 0);
      if (cnt >= MAX_POR_HORA) return _ok({ erro: 'limite de envios por hora atingido' });
      cache.put(bucket, cnt + 1, 3700);

      if (!p.para) return _ok({ erro: 'destinatario vazio' });

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

/** registra o envio numa aba "Propostas" (auditoria), se o script tiver planilha */
function _log(p) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) return;
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
