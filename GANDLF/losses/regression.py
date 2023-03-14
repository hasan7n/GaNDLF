import torch
from torch.nn import MSELoss, CrossEntropyLoss, L1Loss
from GANDLF.utils import one_hot


def CEL(out, target, params):
    """
    Cross entropy loss with optional class weights.

    Args:
        out (torch.Tensor): Output tensor from the model.
        target (torch.Tensor): Target tensor of class labels.
        params (dict): Dictionary of parameters including weights.

    Returns:
        torch.Tensor: Cross entropy loss tensor.
    """
    if len(target.shape) > 1 and target.shape[-1] == 1:
        target = torch.squeeze(target, -1)

    weights = None
    if params.get("weights") is not None:
        # Check that the number of classes matches the number of weights
        num_classes = len(params["weights"])
        if out.shape[-1] != num_classes:
            raise ValueError(f"Number of classes {num_classes} does not match output shape {out.shape[-1]}")
        
        weights = torch.FloatTensor(list(params["weights"].values()))
        weights = weights.float().to(target.device)

    cel = CrossEntropyLoss(weight=weights)
    return cel(out, target)


def CE_Logits(out, target):
    """
    Binary cross entropy loss with logits.

    Args:
        out (torch.Tensor): Output tensor from the model.
        target (torch.Tensor): Target tensor of binary labels.

    Returns:
        torch.Tensor: Binary cross entropy loss tensor.
    """
    if not torch.all(target.byte() == target):
        raise ValueError("Target tensor must be binary (0 or 1)")

    loss = torch.nn.BCEWithLogitsLoss()
    loss_val = loss(out.contiguous().view(-1), target.contiguous().view(-1))
    return loss_val


def CE(out, target):
    """
    Binary cross entropy loss.

    Args:
        out (torch.Tensor): Output tensor from the model.
        target (torch.Tensor): Target tensor of binary labels.

    Returns:
        torch.Tensor: Binary cross entropy loss tensor.
    """
    if not torch.all(target.byte() == target):
        raise ValueError("Target tensor must be binary (0 or 1)")

    loss = torch.nn.BCELoss()
    loss_val = loss(out.contiguous().view(-1).float(), target.contiguous().view(-1).float())
    return loss_val


def CCE_Generic(out, target, params, CCE_Type):
    """
    Generic function to calculate CCE loss

    Args:
        out (torch.tensor): The predicted output value for each pixel. dimension: [batch, class, x, y, z].
        target (torch.tensor): The ground truth label for each pixel. dimension: [batch, class, x, y, z] factorial_class_list.
        params (dict): The parameter dictionary.
        CCE_Type (torch.nn): The CE loss function type.

    Returns:
        torch.tensor: The final loss value after taking multiple classes into consideration
    """

    acc_ce_loss = 0
    target = one_hot(target, params["model"]["class_list"]).type(out.dtype)

    for i in range(0, len(params["model"]["class_list"])):
        curr_ce_loss = CCE_Type(out[:, i, ...], target[:, i, ...])
        if params["weights"] is not None:
            curr_ce_loss = curr_ce_loss * params["weights"][i]
        acc_ce_loss += curr_ce_loss

    # Take the mean of the loss if weights are not provided.
    if params["weights"] is None:
        total_loss = torch.mean(total_loss)

    return acc_ce_loss


def L1(output, label, reduction="mean", scaling_factor=1):
    """
    Calculate the mean square error between the output variable from the network and the target

    Parameters
    ----------
    output : torch.Tensor
        The output generated usually by the network
    target : torch.Tensor
        The label for the corresponding Tensor for which the output was generated
    reduction : string, optional
        DESCRIPTION. The default is 'mean'.
    scaling_factor : integer, optional
        The scaling factor to multiply the label with

    Returns
    -------
    loss : torch.Tensor
        Computed Mean Squared Error loss for the output and label

    """
    scaling_factor = torch.as_tensor(scaling_factor)
    label = label.float()
    label = label * scaling_factor
    loss_fn = L1Loss(reduction=reduction)
    iflat = output.contiguous().view(-1)
    tflat = label.contiguous().view(-1)
    loss = loss_fn(iflat, tflat)
    return loss


def L1_loss(inp, target, params):
    acc_mse_loss = 0
    # if inp.shape != target.shape:
    #     sys.exit('Input and target shapes are inconsistent')

    if inp.shape[0] == 1:
        if params is not None:
            acc_mse_loss += L1(
                inp,
                target,
                reduction=params["loss_function"]["l1"]["reduction"],
                scaling_factor=params["scaling_factor"],
            )
        else:
            acc_mse_loss += L1(inp, target)
        # for i in range(0, params["model"]["num_classes"]):
        #    acc_mse_loss += MSE(inp[i], target[i], reduction=params["loss_function"]['mse']["reduction"])
    else:
        if params is not None:
            for i in range(0, params["model"]["num_classes"]):
                acc_mse_loss += L1(
                    inp[:, i, ...],
                    target[:, i, ...],
                    reduction=params["loss_function"]["mse"]["reduction"],
                    scaling_factor=params["scaling_factor"],
                )
        else:
            for i in range(0, inp.shape[1]):
                acc_mse_loss += L1(inp[:, i, ...], target[:, i, ...])
    if params is not None:
        acc_mse_loss /= params["model"]["num_classes"]
    else:
        acc_mse_loss /= inp.shape[1]

    return acc_mse_loss


def MSE(output, label, reduction="mean", scaling_factor=1):
    """
    Calculate the mean square error between the output variable from the network and the target

    Parameters
    ----------
    output : torch.Tensor
        The output generated usually by the network
    target : torch.Tensor
        The label for the corresponding Tensor for which the output was generated
    reduction : string, optional
        DESCRIPTION. The default is 'mean'.
    scaling_factor : integer, optional
        The scaling factor to multiply the label with

    Returns
    -------
    loss : torch.Tensor
        Computed Mean Squared Error loss for the output and label

    """
    scaling_factor = torch.as_tensor(scaling_factor)
    label = label.float()
    label = label * scaling_factor
    loss_fn = MSELoss(reduction=reduction)
    iflat = output.contiguous().view(-1)
    tflat = label.contiguous().view(-1)
    loss = loss_fn(iflat, tflat)
    return loss


def MSE_loss(inp, target, params):
    acc_mse_loss = 0
    # if inp.shape != target.shape:
    #     sys.exit('Input and target shapes are inconsistent')

    reduction = "mean"
    if params is not None:
        if "mse" in params["loss_function"]:
            if isinstance(params["loss_function"]["mse"], dict):
                reduction = params["loss_function"]["mse"]["reduction"]

    if inp.shape[0] == 1:
        if params is not None:
            acc_mse_loss += MSE(
                inp,
                target,
                reduction=reduction,
                scaling_factor=params["scaling_factor"],
            )
        else:
            acc_mse_loss += MSE(inp, target)
        # for i in range(0, params["model"]["num_classes"]):
        #    acc_mse_loss += MSE(inp[i], target[i], reduction=params["loss_function"]['mse']["reduction"])
    else:
        if params is not None:
            for i in range(0, params["model"]["num_classes"]):
                acc_mse_loss += MSE(
                    inp[:, i, ...],
                    target[:, i, ...],
                    reduction=reduction,
                    scaling_factor=params["scaling_factor"],
                )
        else:
            for i in range(0, inp.shape[1]):
                acc_mse_loss += MSE(inp[:, i, ...], target[:, i, ...])
    if params is not None:
        acc_mse_loss /= params["model"]["num_classes"]
    else:
        acc_mse_loss /= inp.shape[1]

    return acc_mse_loss
